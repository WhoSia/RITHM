# frozen_string_literal: true
# RITHM information-filtration-safe individual history features.
# informed: false NEVER reads num_a or latent congestion cost.
module RithmLearning
  module_function

  def features(rows, informed: true)
    seen = Hash.new(0)
    seen_route_state = Hash.new(0)
    switches = 0
    prev_route = nil
    prev_n = nil
    total_observed = 0.0
    out = []
    rows.each_with_index do |row, t|
      route = Integer(row.fetch(:route_a))
      raise ArgumentError, 'invalid route' unless [0, 1].include?(route)
      # Chosen-action realized payoff is publicly observed for both types.
      # Do not substitute hidden route cost for payoffs for uninformed persons.
      feedback = if informed
                   Float(row.fetch(:cost))
                 else
                   Float(row.fetch(:payoff))
                 end
      n = informed ? Integer(row.fetch(:num_a)) : nil
      raise ArgumentError, 'invalid congestion' if informed && !(0..6).cover?(n)
      if t.positive?
        datum = {
          period: Integer(row.fetch(:period)),
          previous_route: prev_route,
          prior_switch_rate: switches.fdiv([t - 1, 1].max),
          previous_mean_feedback: total_observed.fdiv(t),
          feedback_kind: informed ? :chosen_route_cost : :received_payoff,
          switched: (route == prev_route ? 0 : 1)
        }
        if informed
          datum.merge!(
            previous_n: prev_n,
            previous_relative_cost: prev_route == 1 ? 3 * prev_n - 12 : 12 - 3 * prev_n,
            familiarity: seen.fetch(prev_n, 0),
            route_state_familiarity: seen_route_state.fetch([prev_n, prev_route], 0)
          )
        end
        out << datum
        switches += datum[:switched]
      end
      if informed
        seen[n] += 1
        seen_route_state[[n, route]] += 1
      end
      prev_route = route
      prev_n = n
      total_observed += feedback
    end
    out
  end
end
