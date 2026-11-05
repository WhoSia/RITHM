# frozen_string_literal: true
# RITHM 2.10 P3-R13. Source-free, exact six-actor welfare-error attribution.
# Signed routes: +1 for B->A, -1 for A->B. No causal dependence inference.
module Rithm210GroupResidualWelfare
  module_function

  def analyze(routes, switches, probabilities)
    raise ArgumentError, 'six actors required' unless [routes, switches, probabilities].all? { |v| v.is_a?(Array) && v.size == 6 }
    raise ArgumentError, 'routes must start at nA=4' unless routes.all? { |v| v == 0 || v == 1 } && routes.sum == 4
    raise ArgumentError, 'binary outcomes required' unless switches.all? { |v| v == 0 || v == 1 }
    raise ArgumentError, 'probabilities outside [0,1]' unless probabilities.all? { |p| p.is_a?(Numeric) && p.finite? && p.between?(0, 1) }

    sign = routes.map { |r| r == 0 ? 1 : -1 }
    residual = switches.zip(probabilities).map { |y, p| y - p }
    mean_net = sign.zip(probabilities).sum { |s, p| s * p }
    residual_net = sign.zip(residual).sum { |s, e| s * e }
    observed_net = sign.zip(switches).sum { |s, y| s * y }
    predicted_loss = 3.0 * (mean_net**2 + probabilities.sum { |p| p * (1 - p) })
    observed_loss = 3 * observed_net**2

    linear = 6.0 * mean_net * residual_net
    diagonal = 3.0 * residual.each_with_index.sum { |e, i| e**2 - probabilities[i] * (1 - probabilities[i]) }
    same = 0.0
    opposite = 0.0
    same_pairs = 0
    opposite_pairs = 0
    6.times do |i|
      (i + 1...6).each do |j|
        product = residual[i] * residual[j]
        if sign[i] == sign[j]
          same += 6.0 * product
          same_pairs += 1
        else
          opposite -= 6.0 * product
          opposite_pairs += 1
        end
      end
    end
    total = linear + diagonal + same + opposite
    raise 'welfare identity violated' unless (observed_loss - predicted_loss - total).abs < 1e-9

    {observed_loss: observed_loss, predicted_loss: predicted_loss,
     welfare_error: observed_loss - predicted_loss,
     linear_calibration: linear, diagonal_calibration: diagonal,
     same_route_pair: same, opposite_route_pair: opposite,
     same_pair_mean_residual: same / (6.0 * same_pairs),
     opposite_pair_mean_residual: -opposite / (6.0 * opposite_pairs),
     mean_switch_error: residual.sum / 6.0,
     gross_observed: switches.sum, gross_predicted: probabilities.sum,
     zero_observed: switches.sum.zero? ? 1 : 0,
     signed_net_observed: observed_net, signed_net_predicted: mean_net}
  end

  def aggregate(rows)
    raise ArgumentError, 'empty group sample' if rows.empty?
    keys = [:observed_loss, :predicted_loss, :welfare_error, :linear_calibration,
            :diagonal_calibration, :same_route_pair, :opposite_route_pair,
            :same_pair_mean_residual, :opposite_pair_mean_residual,
            :mean_switch_error, :gross_observed, :gross_predicted, :zero_observed]
    means = keys.to_h { |k| [k, rows.sum { |row| row.fetch(k) }.fdiv(rows.size)] }
    {n: rows.size, **means}
  end
end
