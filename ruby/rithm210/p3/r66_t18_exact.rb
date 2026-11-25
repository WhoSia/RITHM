# frozen_string_literal: true
require_relative 'r66_t18_learning'
module RithmT18
  module Exact
    module_function
    BASE=[1,10,40,80,80,32].map { |x| Rational(x,243) }.freeze
    LOW=Rational(1,4); HIGH=Rational(13,20)
    def odds(history,low:LOW,high:HIGH)
      raise ArgumentError,'history/grid' unless !history.empty? && history.all? { |k| (0..5).include?(k) } && 0<=low && low<high && high<1
      history.each_cons(2).reduce(Rational(1)) do |o,(k,j)|
        o*(high*(k==j ? 1 : 0)+(1-high)*BASE[j])/(low*(k==j ? 1 : 0)+(1-low)*BASE[j])
      end
    end
    def rho(history,low:LOW,high:HIGH)
      o=odds(history,low:low,high:high); (low+high*o)/(1+o)
    end
    # Both histories have current K=4, same own A route/duration and feasible identical payoff sequence.
    def gain(history,**grid)
      -1+rho(history,**grid)*(3*history.last-10)
    end
    # Common eligibility p=1/2, full disclosure, strict gain, response=1, zero threshold.
    # For LOW>1/5, once all actors enter {0,6}, all prefer a flip at every common opportunity.
    def exact_common(horizon:40,low:LOW,high:HIGH)
      raise ArgumentError,'horizon/grid' unless horizon.is_a?(Integer) && horizon>=1 && low>Rational(1,5) && high>Rational(1,2) && (low+high)/2<=Rational(1,2) && high<1
      m=0; m+=1 while rho(Array.new(m+1,4),low:low,high:high)<=Rational(1,2)
      p=[Rational(1),Rational(0),Rational(0)] # state 5,0,6
      total=0
      horizon.times do |t|
        total+=3*p[0]+48*p[1]+12*p[2]
        next if t<m || t==horizon-1
        p=[p[0]/2,(p[0]+p[1]+p[2])/2,(p[1]+p[2])/2]
      end
      {first_eligible_observation:m,expected_cost:total,final:p}
    end
  end
end
