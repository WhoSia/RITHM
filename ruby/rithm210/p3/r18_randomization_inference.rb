# frozen_string_literal: true
# RITHM R18-P1 — cluster-level 2x2 randomization inference (source-free).
# Sharp-null Fisher p-values; randomization occurs at independent SESSION level.
module Rithm210R18RandomizationInference
  module_function
  ARMS = [:lagged_frozen, :lagged_feedback, :current_frozen, :current_feedback].freeze
  SIGNS = { lagged_frozen: 1.0, lagged_feedback: -1.0,
            current_frozen: -1.0, current_feedback: 1.0 }.freeze

  def validate(assignment, outcome, require_replicates: false)
    raise ArgumentError, 'empty assignment' if assignment.empty?
    raise ArgumentError, 'mismatched keys' unless assignment.keys.sort == outcome.keys.sort
    counts = ARMS.to_h { |a| [a, 0] }
    assignment.each do |id, arm|
      raise ArgumentError, 'invalid arm' unless counts.key?(arm)
      y = outcome[id]
      raise ArgumentError, 'outcome must be finite' unless y.is_a?(Numeric) && y.finite?
      counts[arm] += 1
    end
    raise ArgumentError, 'unbalanced arms' unless counts.values.uniq.size == 1
    raise ArgumentError, 'replicates required for variance' if require_replicates && counts.values.first < 2
    counts.values.first
  end

  def estimate(assignment, outcome)
    m = validate(assignment, outcome)
    mean = ARMS.to_h do |a|
      ids = assignment.keys.select { |id| assignment[id] == a }
      [a, ids.sum { |id| outcome.fetch(id).to_f } / m]
    end
    { interaction: SIGNS.sum { |arm, sign| sign * mean.fetch(arm) },
      means: mean, per_arm: m }
  end

  def neyman_variance(assignment, outcome)
    m = validate(assignment, outcome, require_replicates: true)
    ARMS.sum do |a|
      values = assignment.keys.select { |id| assignment[id] == a }.map { |id| outcome.fetch(id).to_f }
      avg = values.sum / m
      sample_var = values.sum { |x| (x - avg)**2 } / (m - 1).to_f
      sample_var / m
    end
  end

  def balanced_assignments(ids)
    raise ArgumentError, 'exact engine supports 4 or 8 clusters' unless [4, 8].include?(ids.size) && ids.uniq.size == ids.size
    m = ids.size / 4
    Enumerator.new do |y|
      walk = lambda do |index, counts, acc|
        if index == ids.size
          y << acc.dup
          return
        end
        ARMS.each do |arm|
          next if counts[arm] >= m
          counts[arm] += 1
          acc[ids[index]] = arm
          walk.call(index + 1, counts, acc)
          counts[arm] -= 1
          acc.delete(ids[index])
        end
      end
      walk.call(0, ARMS.to_h { |a| [a, 0] }, {})
    end
  end

  def shuffled_assignment(ids, rng)
    shuffled = ids.shuffle(random: rng)
    m = ids.length / 4
    shuffled.each_with_index.to_h { |id, i| [id, ARMS[i / m]] }
  end

  def fisher_sharp_null(assignment, outcome, draws: 20_000, seed: 20261105)
    m = validate(assignment, outcome)
    ids = assignment.keys
    observed = estimate(assignment, outcome)[:interaction]
    raise ArgumentError, 'draws must be positive' unless draws.is_a?(Integer) && draws > 0
    if ids.size <= 8
      dist = balanced_assignments(ids).map { |a| estimate(a, outcome)[:interaction] }
      extreme = dist.count { |v| v.abs >= observed.abs - 1e-10 }
      return { observed: observed, p_two_sided: extreme.to_f / dist.size,
               assignments: dist.size, method: 'exact Fisher sharp-null', per_arm: m }
    end
    rng = Random.new(seed)
    extreme = 0
    draws.times do
      trial = shuffled_assignment(ids, rng)
      extreme += 1 if estimate(trial, outcome)[:interaction].abs >= observed.abs - 1e-10
    end
    { observed: observed, p_two_sided: (extreme + 1.0) / (draws + 1.0),
      assignments: draws, method: 'Monte Carlo Fisher sharp-null, add-one', per_arm: m }
  end

  def randomize_sessions(session_ids, seed: 20261105)
    raise ArgumentError, 'sessions must be unique, nonempty, multiple of four' unless
      session_ids.uniq.size == session_ids.size && !session_ids.empty? && session_ids.size % 4 == 0
    shuffled_assignment(session_ids, Random.new(seed))
  end
end
