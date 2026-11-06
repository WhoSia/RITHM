# frozen_string_literal: true
# R21: strictly prior-only EWA-type cost-attraction candidate; not authors' fitted EWA.
require 'csv'
require 'digest'
require 'json'
require_relative 'r20_group_bridge'

module Rithm210R21EWAGroupCV
  module_function
  SHA = Rithm210R20GroupBridge::SHA
  Params = Struct.new(:phi, :rho, :delta, :beta, keyword_init: true) do
    def label
      "p#{phi}_r#{rho}_d#{delta}_b#{beta}"
    end
  end

  class Learner
    def initialize(p)
      @p = p
      @n = @a = @b = 0.0
    end

    def prob_a
      z = @p.beta * (@a - @b)
      z >= 0 ? 1.0 / (1.0 + Math.exp(-z)) : Math.exp(z) / (1.0 + Math.exp(z))
    end

    def update(route_a:, n_a:, informed:)
      raise ArgumentError, 'bools required' unless [true, false].include?(route_a) && [true, false].include?(informed)
      raise ArgumentError, 'occupancy' unless n_a.is_a?(Integer) && n_a.between?(0, 6)
      other_a = n_a - (route_a ? 1 : 0)
      raise ArgumentError, 'impossible route' unless other_a.between?(0, 5)
      den = @p.rho * @n + 1.0
      wa = route_a ? 1.0 : (informed ? @p.delta : 0.0)
      wb = route_a ? (informed ? @p.delta : 0.0) : 1.0
      @a = (@p.phi * @n * @a - wa * (other_a + 1)) / den
      @b = (@p.phi * @n * @b - wb * (2 * (6 - other_a))) / den
      @n = den
    end
  end

  def grid
    [0.5, 0.9].product([0.5, 1.0], [0.0, 0.8], [0.3, 0.8, 1.5]).map do |phi, rho, delta, beta|
      Params.new(phi: phi, rho: rho, delta: delta, beta: beta)
    end
  end

  def source(path)
    raise 'source SHA mismatch' unless Digest::SHA256.file(path).hexdigest == SHA
    groups = Hash.new { |h, k| h[k] = [] }
    CSV.foreach(path, headers: true) do |r|
      s = r.fetch('session').to_i
      t = r.fetch('Period').to_i
      next if [2, 101].include?(s) || !r.fetch('trt').to_i.between?(1, 3) || !t.between?(1, 40)
      groups[[s, r.fetch('section').to_i, t, r.fetch('Group').to_i]] << r
    end
    raise '5760 complete groups expected' unless groups.size == 5760 && groups.values.all? { |rs| rs.size == 6 }
    groups
  end

  def predict_scores(groups, params, blend: 1.0)
    raise ArgumentError, 'blend 0..1' unless blend.is_a?(Numeric) && blend.finite? && blend.between?(0, 1)
    states = {}
    choices = {}
    rows = []
    groups.keys.sort.each do |s, section, period, group|
      people = groups.fetch([s, section, period, group]).sort_by { |r| r.fetch('ID').to_i }
      raise 'duplicate actor' unless people.map { |r| r.fetch('ID').to_i }.uniq.size == 6
      treatment = people.first.fetch('trt').to_i
      raise 'mixed treatments' unless people.all? { |r| r.fetch('trt').to_i == treatment }
      n = people.sum { |r| r.fetch('RouteA').to_i }
      raise 'inconsistent occupancy' unless people.all? { |r| r.fetch('NumA').to_i == n }
      current = people.map do |r|
        key = [s, section, r.fetch('ID').to_i]
        state = states[key] ||= Learner.new(params)
        [state, r.fetch('RouteA').to_i == 1, r.fetch('Informed') == '1', key]
      end
      # Prediction first, six simultaneous updates second.
      ps = current.map do |state, _, _, key|
        a_count, prior = choices.fetch(key, [0, 0])
        own = (a_count + 1).to_f / (prior + 2)
        blend * state.prob_a + (1 - blend) * own
      end
      rows << {session: s, treatment: treatment, group: group, period: period,
               **Rithm210R20GroupBridge.score(ps, n)}
      current.each do |state, route_a, informed, key|
        state.update(route_a: route_a, n_a: n, informed: informed)
        a_count, prior = choices.fetch(key, [0, 0])
        choices[key] = [a_count + (route_a ? 1 : 0), prior + 1]
      end
    end
    rows
  end

  def cross_validate(path, candidates: grid)
    raise ArgumentError, 'candidate list' unless candidates.is_a?(Array) && !candidates.empty?
    groups = source(path)
    sessions = groups.keys.map(&:first).uniq.sort
    raise '24 independent sessions expected' unless sessions.size == 24
    folds = sessions.each_with_index.to_h { |s, i| [s, i % 6] }
    scored = candidates.to_h do |p|
      rs = predict_scores(groups, p)
      [p.label, rs.group_by { |r| [r[:session], r[:treatment]] }.transform_values do |v|
        Rithm210R20GroupBridge.summary(v)
      end]
    end
    holdout = []
    6.times do |fold|
      test = sessions.select { |s| folds[s] == fold }
      train = sessions - test
      (1..3).each do |treatment|
        best = candidates.min_by do |p|
          values = train.map { |s| scored.fetch(p.label).fetch([s, treatment])[:logloss] }
          [values.sum / values.size, p.label]
        end
        test.each do |sid|
          holdout << {session: sid, treatment: treatment, fold: fold, param: best.label,
                      **scored.fetch(best.label).fetch([sid, treatment])}
        end
      end
    end
    results = holdout.group_by { |r| r[:treatment] }.to_h do |trt, rs|
      [trt, {sessions: rs.size, groups: rs.sum { |r| r[:groups] },
             logloss: rs.sum { |r| r[:logloss] } / rs.size,
             brier: rs.sum { |r| r[:brier] } / rs.size,
             cost_abs_error: rs.sum { |r| r[:cost_abs_error] } / rs.size,
             chosen: rs.group_by { |r| r[:param] }.transform_values(&:size)}]
    end
    {sessions: sessions.size, candidates: candidates.size, models: results,
     session_results: holdout, caveat: 'EWA-type cost attraction, session-separated parameter selection; not original-author full EWA.'}
  end
end

puts JSON.pretty_generate(Rithm210R21EWAGroupCV.cross_validate(ARGV.fetch(0))) if __FILE__ == $PROGRAM_NAME
