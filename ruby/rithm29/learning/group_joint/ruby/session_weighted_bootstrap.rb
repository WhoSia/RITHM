# frozen_string_literal: true
# RITHM-2.9: paired whole-session bootstrap with explicit estimand.
# Self-contained standard-library Ruby; never resample individuals across sessions.
module RithmSessionWeightedBootstrap
  module_function
  def estimate(rows, estimand: :transition_weighted)
    validate!(rows)
    case estimand
    when :transition_weighted
      rows.sum { |r| r.fetch(:n) * (r.fetch(:candidate) - r.fetch(:baseline)) } / rows.sum { |r| r.fetch(:n) }.to_f
    when :equal_session
      rows.sum { |r| r.fetch(:candidate) - r.fetch(:baseline) } / rows.length.to_f
    else
      raise ArgumentError, 'unknown estimand'
    end
  end
  def interval(rows, estimand: :transition_weighted, draws: 20_000, seed: 20261101)
    validate!(rows)
    raise ArgumentError, 'draws must be >= 100' unless draws.is_a?(Integer) && draws >= 100
    point = estimate(rows, estimand: estimand)
    rng = Random.new(seed)
    n = rows.length
    samples = Array.new(draws) do
      sample = Array.new(n) { rows.fetch(rng.rand(n)) }
      estimate(sample, estimand: estimand)
    end.sort
    {mean: point, lower: samples[((draws - 1)*0.025).floor],
      upper: samples[((draws - 1)*0.975).ceil], units: n, estimand: estimand}
  end
  def validate!(rows)
    raise ArgumentError, 'empty sessions' if rows.empty?
    rows.each do |r|
      raise ArgumentError, 'n must be positive integer' unless r[:n].is_a?(Integer) && r[:n] > 0
      [:baseline, :candidate].each do |key|
        raise ArgumentError, "nonfinite #{key}" unless r[key].is_a?(Numeric) && r[key].finite?
      end
    end
  end
end
