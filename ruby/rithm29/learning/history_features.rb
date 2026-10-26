# frozen_string_literal: true
# RITHM: pre-decision history features, independent of proprietary model fits.
# Feed chronological rows from one participant; Ruby stdlib only.
module RithmLearning
  module_function
  def features(rows)
    seen = Hash.new(0)
    seen_route_state = Hash.new(0)
    switches = 0
    previous_route = nil
    previous_n = nil
    prior_cost_sum = 0.0
    out = []
    rows.each_with_index do |row, t|
      route = Integer(row.fetch(:route_a))
      n = Integer(row.fetch(:num_a))
      cost = Float(row.fetch(:cost))
      raise ArgumentError, 'invalid route/number' unless [0, 1].include?(route) && (0..6).cover?(n)
      if t.positive?
        diff = previous_route == 1 ? 3 * previous_n - 12 : 12 - 3 * previous_n
        out << {
          period: Integer(row.fetch(:period)),
          previous_route: previous_route,
          previous_n: previous_n,
          previous_relative_cost: diff,
          familiarity: seen.fetch(previous_n, 0),
          route_state_familiarity: seen_route_state.fetch([previous_n, previous_route], 0),
          prior_switch_rate: switches.fdiv(t > 1 ? t - 1 : 1),
          previous_mean_cost: prior_cost_sum.fdiv(t),
          switched: (route != previous_route ? 1 : 0)
        }
        switches += out.last[:switched]
      end
      seen[n] += 1
      seen_route_state[[n, route]] += 1
      previous_route = route
      previous_n = n
      prior_cost_sum += cost
    end
    out
  end
end
