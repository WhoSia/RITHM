# frozen_string_literal: true
module RithmT13
  module Identification
    module_function
    def positive_gain_flip(opportunity:,attention:,respond:Rational(2,5))
      o=Rational(opportunity);q=Rational(attention);r=Rational(respond)
      raise ArgumentError,'probability out of range' unless [o,q,r].all? { |x| x.between?(0,1) }
      o*q*r
    end
    def exact_equivalent_cases
      a=positive_gain_flip(opportunity:Rational(1,2),attention:Rational(1,2))
      b=positive_gain_flip(opportunity:Rational(1,4),attention:1)
      raise 'not equivalent' unless a==b
      {a:a,b:b,same_marginal:true,distinct_opportunity:true,distinct_attention:true}
    end
  end
end
