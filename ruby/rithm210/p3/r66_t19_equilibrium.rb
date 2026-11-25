# frozen_string_literal: true
# Common revision opportunity, old nA=5, independent mixing within old routes.
# Kappa is subjective switch disutility, not real resource loss in the congestion metric.
module RithmT19
  module Equilibrium
    module_function
    def gains(a,b,kappa)
      a,b,k=[a,b,kappa].map { |x| Rational(x) }
      raise ArgumentError,'parameters' unless a.between?(0,1) && b.between?(0,1) && k>=0
      [1-12*a+3*b-k,-4+15*a-k]
    end
    def best_response?(p,g)
      p==0 ? g<=0 : p==1 ? g>=0 : g==0
    end
    def equilibria(kappa)
      k=Rational(kappa); raise ArgumentError,'threshold' if k<0
      branches={low:[[(1-k)/12,0].max,Rational(0)]}
      if k<=Rational(4,9)
        branches[:high]=[(4-k)/12,Rational(1)]
        branches[:interior]=[(4+k)/15,(11+9*k)/15]
      end
      branches.values.uniq.each do |a,b|
        raise 'not equilibrium' unless gains(a,b,k).zip([a,b]).all? { |g,p| best_response?(p,g) }
      end
      branches
    end
    def congestion(a,b)
      a,b=[a,b].map { |x| Rational(x) }
      raise ArgumentError,'probabilities' unless a.between?(0,1) && b.between?(0,1)
      mean=5-5*a+b;var=5*a*(1-a)+b*(1-b)
      3*((mean-4)**2+var)
    end
    def resource_cost(a,b,c)
      a,b,c=[a,b,c].map { |x| Rational(x) }
      raise ArgumentError,'resource cost' if c<0
      congestion(a,b)+c*(5*a+b)
    end
    def pure(kappa)
      k=Rational(kappa);raise ArgumentError,'threshold' if k<0
      (0...64).filter_map do |mask|
        n=6.times.count { |i| mask[i]==1 }
        ok=6.times.all? do |i|
          old_a=i<5;new_a=mask[i]==1;other=n-(new_a ? 1 : 0)
          a_cost=other+1+(old_a ? 0 : k);b_cost=2*(6-other)+(old_a ? k : 0)
          new_a ? a_cost<=b_cost : b_cost<=a_cost
        end
        {mask:mask,n:n,cost:3*(n-4)**2,switches:6.times.count { |i| (mask[i]==1)!=(i<5) }} if ok
      end
    end
  end
end
