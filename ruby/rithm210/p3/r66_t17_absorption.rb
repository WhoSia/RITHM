# frozen_string_literal: true
require_relative 'r66_t17_oracle'
module RithmT17
  module Absorption
    module_function
    # At n=5, A actors face K=4 and the B actor faces K=5.
    # Full previous-state disclosure; strict improvement; response and eligibility positive.
    def gains_at_five(rho)
      r=Oracle.probability(rho)
      [2*r-1,1-5*r]
    end
    def interval(threshold=0)
      c=Rational(threshold);raise ArgumentError,'threshold' if c<0
      [[0,(1-c)/5].max,[1,(1+c)/2].min]
    end
    def trapped?(rho,threshold=0)
      r=Oracle.probability(rho);lo,hi=interval(threshold)
      r.between?(lo,hi)
    end
  end
end
