# frozen_string_literal: true
require_relative 'r66_t16_belief'
module RithmT16
  module Filter
    module_function
    B=Belief
    # Controlled observation: own action is a given, not extra evidence about K.
    # Transition is a subjective exogenous persistence/reset model, not a game equilibrium.
    def replay(observations,initial:B.binomial_base,persistence:,base:B.binomial_base)
      prior=B.normalize(initial)
      observations.map do |obs|
        route=obs.fetch(:route); payoff=obs.fetch(:payoff)
        posterior=B.posterior(prior,route,payoff)
        if obs.key?(:observed_k)
          k=obs.fetch(:observed_k)
          raise ArgumentError,'inconsistent or impossible disclosed state' unless B::STATES.include?(k) && posterior[k]>0
          posterior=B::STATES.map { |j| Rational(j==k ? 1 : 0) }.freeze
        end
        next_prior=B.predict(posterior,persistence:persistence,base:base)
        record={prior:prior,posterior:posterior,next_prior:next_prior,next_gain:B.expected_gain(next_prior,route)}
        prior=next_prior
        record
      end
    end
  end
end
