# frozen_string_literal: true
require_relative 'r66_t16_belief'
module RithmT16
  module SignalValue
    module_function
    B=Belief
    # Integrate exact continuous-payoff density over intervals with constant likelihood.
    def evaluate(prior,route,persistence:,base:,threshold:0)
      p=B.normalize(prior); c=Rational(threshold)
      raise ArgumentError,'threshold' if c<0
      cuts=B::STATES.flat_map { |k| [6-B.cost(k,route),16-B.cost(k,route)] }.uniq.sort
      total=0; payoff_value=0; disclosure_value=0
      cuts.each_cons(2) do |lo,hi|
        y=Rational(lo+hi,2)
        weights=B::STATES.map { |k| (6..16).cover?(y+B.cost(k,route)) ? p[k] : 0 }
        mass=weights.sum*Rational(hi-lo,10)
        next if mass.zero?
        q=B.normalize(weights)
        payoff_value+=mass*[B.expected_gain(B.predict(q,persistence:persistence,base:base),route)-c,0].max
        disclosure_value+=mass*B.previous_state_information_value(q,route,persistence:persistence,base:base,threshold:c)
        total+=mass
      end
      raise 'mass leak' unless total==1
      blind=[B.expected_gain(B.predict(p,persistence:persistence,base:base),route)-c,0].max
      full=blind+B.previous_state_information_value(p,route,persistence:persistence,base:base,threshold:c)
      raise 'value decomposition failed' unless full==payoff_value+disclosure_value
      {blind:blind,payoff:payoff_value,full:full,payoff_increment:payoff_value-blind,disclosure_increment:disclosure_value}
    end
  end
end
