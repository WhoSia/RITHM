# frozen_string_literal: true
# Eligible, strictly profitable opportunities; elapsed calendar dates are NOT exposures.
module RithmT15
  module Spell
    module_function
    P = [Rational(1,4), Rational(3,4)].freeze
    def posterior(failures, successes=0)
      raise ArgumentError, 'nonnegative integer counts' unless [failures,successes].all? { |n| n.is_a?(Integer) && n >= 0 }
      w=P.map { |p| (1-p)**failures*p**successes }
      w.map { |v| v/w.sum }
    end
    def hazard(failures, successes=0)
      posterior(failures,successes).zip(P).sum { |w,p| w*p }
    end
    def survival(k)
      raise ArgumentError, 'nonnegative integer exposures' unless k.is_a?(Integer) && k>=0
      P.sum { |p| (1-p)**k }/2
    end
    def renewal_survival(k)
      raise ArgumentError, 'nonnegative integer exposures' unless k.is_a?(Integer) && k>=0
      (0...k).reduce(Rational(1)) { |v,j| v*(1-hazard(j)) }
    end
    # Conditional on k failures followed by a switch, compare the next eligible profitable opportunity.
    def after_switch(k, mechanism)
      case mechanism
      when :fixed then hazard(k,1)
      when :reset then hazard(0)
      else raise ArgumentError, 'mechanism'
      end
    end
  end
end
