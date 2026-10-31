# frozen_string_literal: true
# Source-observable one-step inertia offset; no fitting on held-out labels.
module RithmInertiaCalibration
  module_function
  def adjusted_probability(p, previous_a, kappa)
    raise ArgumentError, 'p' unless p.is_a?(Numeric) && p.finite? && p.between?(0.0, 1.0)
    raise ArgumentError, 'previous_a' unless [0, 1].include?(previous_a)
    raise ArgumentError, 'kappa' unless kappa.is_a?(Numeric) && kappa.finite? && kappa >= 0
    return p if kappa == 0
    return p if p == 0.0 || p == 1.0
    z = Math.log(p / (1.0 - p)) + kappa * (2 * previous_a - 1)
    z >= 0 ? 1.0 / (1.0 + Math.exp(-z)) : Math.exp(z) / (1.0 + Math.exp(z))
  end
  def switch_probability(p, previous_a, kappa)
    pa = adjusted_probability(p, previous_a, kappa)
    previous_a == 1 ? 1.0 - pa : pa
  end
end
