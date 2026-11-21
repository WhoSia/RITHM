# frozen_string_literal: true
require_relative 'r66_t13_identification'
module RithmT13
  module FactorialDesign
    module_function
    # Positive-gain hazard under independently controlled opportunity / attention.
    def expected_switch(opportunity:,attention:,respond:Rational(2,5),lapse:Rational(1,50))
      o,q,r,l=[opportunity,attention,respond,lapse].map { |x| Rational(x) }
      raise ArgumentError,'probabilities' unless [o,q,r,l].all? { |x| x.between?(0,1) }
      o*(l+q*(r-l))
    end
    def recover_attention(observed_switch:,known_opportunity:,respond:Rational(2,5),lapse:Rational(1,50))
      p,o,r,l=[observed_switch,known_opportunity,respond,lapse].map { |x| Rational(x) }
      raise ArgumentError,'non-identification' if o.zero? || r==l
      q=(p/o-l)/(r-l)
      raise ArgumentError,'incompatible observation' unless q.between?(0,1)
      q
    end
    def point_counterexample
      p1=expected_switch(opportunity:Rational(1,2),attention:Rational(1,2),lapse:0)
      p2=expected_switch(opportunity:Rational(1,4),attention:1,lapse:0)
      raise 'failed equivalence' unless p1==p2
      {marginal_switch:p1,opportunity_a:Rational(1,2),attention_a:Rational(1,2),
       opportunity_b:Rational(1,4),attention_b:1}
    end
  end
end
