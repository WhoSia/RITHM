# frozen_string_literal: true
# Falsifiable one-period common-freeze mixture over a six-person turnover law.
# Mathematical diagnostic, not a measured cognitive or social mechanism.
module Rithm210ActivityMixture
  module_function
  ZERO = [0, 0].freeze
  def validate(law)
    raise ArgumentError, 'empty joint law' unless law.is_a?(Hash) && !law.empty?
    raise ArgumentError, 'mass not normalized' unless (law.values.sum - 1).abs < 1e-10
    law.each do |(u, d), p|
      raise ArgumentError, 'invalid event' unless u.is_a?(Integer) && d.is_a?(Integer) && u >= 0 && d >= 0
      raise ArgumentError, 'invalid probability' unless p.is_a?(Numeric) && p.finite? && p >= 0
    end
    true
  end
  def freeze(law, z)
    validate(law)
    raise ArgumentError, 'freeze probability outside unit interval' unless z.is_a?(Numeric) && z.finite? && z.between?(0, 1)
    out = law.transform_values { |p| (1 - z) * p }
    out[ZERO] = out.fetch(ZERO, 0) + z
    validate(out)
    out
  end
  def event_metrics(law, current_a: 4)
    validate(law)
    raise ArgumentError, 'invalid current count' unless current_a.is_a?(Integer) && current_a.between?(0, 6)
    out = { zero: 0, cancel: 0, gross: 0, next_excess: 0, drift: 0 }
    current_loss = 3 * (current_a - 4)**2
    law.each do |(u, d), p|
      raise ArgumentError, 'infeasible group transition' unless u <= 6 - current_a && d <= current_a
      next_loss = 3 * (current_a + u - d - 4)**2
      out[:zero] += p if u.zero? && d.zero?
      out[:cancel] += p if u == d && u.positive?
      out[:gross] += (u + d) * p
      out[:next_excess] += next_loss * p
      out[:drift] += (next_loss - current_loss) * p
    end
    out
  end
  def freeze_required(base_zero:, target_zero:)
    [base_zero, target_zero].each do |p|
      raise ArgumentError, 'invalid event probability' unless p.is_a?(Numeric) && p.finite? && p.between?(0, 1)
    end
    return nil if target_zero < base_zero
    return 0 if base_zero == 1 && target_zero == 1
    return nil if base_zero == 1
    (target_zero - base_zero) / (1 - base_zero)
  end
  def restrictions(baseline, target_zero:)
    validate(baseline)
    a = event_metrics(baseline)
    z = freeze_required(base_zero: a[:zero], target_zero: target_zero)
    return { feasible: false, baseline: a, reason: 'target no-switch below baseline' } if z.nil?
    b = event_metrics(freeze(baseline, z))
    raise 'gross-turnover restriction failed' unless (b[:gross] - (1 - z) * a[:gross]).abs < 1e-10
    raise 'cancellation restriction failed' unless (b[:cancel] - (1 - z) * a[:cancel]).abs < 1e-10
    raise 'welfare-drift restriction failed' unless (b[:drift] - (1 - z) * a[:drift]).abs < 1e-10
    { feasible: true, z: z, baseline: a, counterfactual: b,
      falsifiable_rules: %w[nonzero_event_mass_scales gross_and_cancellation_scale welfare_drift_scales] }
  end
end
