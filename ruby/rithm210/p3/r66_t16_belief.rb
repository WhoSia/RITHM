# frozen_string_literal: true
# K = number of OTHER actors on A, 0..5. Ideal continuous V~U[6,16].
module RithmT16
  module Belief
    module_function
    STATES = (0..5).freeze
    def cost(k, route)
      raise ArgumentError,'state' unless k.is_a?(Integer) && STATES.include?(k)
      case route
      when :a then k+1
      when :b then 2*(6-k)
      else raise ArgumentError,'route'
      end
    end
    def gain(k, route)
      cost(k,route)-cost(k,route==:a ? :b : :a)
    end
    def normalize(w)
      raise ArgumentError,'six nonnegative weights' unless w.length==6 && w.all? { |x| x>=0 }
      s=w.sum
      raise ArgumentError,'zero evidence' if s==0
      w.map { |x| Rational(x)/s }.freeze
    end
    def posterior(prior,route,payoff)
      p=normalize(prior); y=Rational(payoff)
      normalize(STATES.map { |k| (6..16).cover?(y+cost(k,route)) ? p[k] : 0 })
    end
    def predict(posterior, persistence:, base:)
      p=normalize(posterior); b=normalize(base); r=Rational(persistence)
      raise ArgumentError,'persistence' unless r.between?(0,1)
      STATES.map { |k| r*p[k]+(1-r)*b[k] }.freeze
    end
    def expected_gain(prior,route)
      normalize(prior).each_with_index.sum { |p,k| p*gain(k,route) }
    end
    # value of perfect information about previous K, with uncertain next K.
    def previous_state_information_value(prior,route,persistence:,base:,threshold:0)
      p=normalize(prior); c=Rational(threshold)
      raise ArgumentError,'threshold' if c<0
      no=[expected_gain(predict(p,persistence:persistence,base:base),route)-c,0].max
      yes=STATES.sum do |k|
        delta=STATES.map { |j| k==j ? 1 : 0 }
        p[k]*[expected_gain(predict(delta,persistence:persistence,base:base),route)-c,0].max
      end
      yes-no
    end
    def binomial_base
      [1,10,40,80,80,32].map { |x| Rational(x,243) }
    end
  end
end
