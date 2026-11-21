# frozen_string_literal: true
# Six-person revision-opportunity laws. These are not information receipts.
module RithmT12
  N = 6
  MASKS = (0...(1 << N)).freeze
  module Schedules
    module_function
    def choose(n,k)
      return 0 if k.negative? || k > n
      (1..k).inject(1) { |acc,j| acc * (n-j+1)/j }
    end
    def validate(weights)
      raise ArgumentError,'64 probabilities required' unless weights.length == (1 << N)
      raise ArgumentError,'negative probability' if weights.any? { |p| Rational(p).negative? }
      raise ArgumentError,'weights must sum to 1' unless weights.sum(Rational(0)) == 1
      weights.map { |p| Rational(p) }.freeze
    end
    def common(theta=Rational(1,2))
      theta=Rational(theta)
      raise ArgumentError,'theta in [0,1]' unless theta.between?(0,1)
      w=Array.new(1<<N,Rational(0))
      w[0]=1-theta
      w[(1<<N)-1]=theta
      validate(w)
    end
    def independent(theta=Rational(1,2))
      theta=Rational(theta)
      raise ArgumentError,'theta in [0,1]' unless theta.between?(0,1)
      validate(MASKS.map { |m| theta**popcount(m)*(1-theta)**(N-popcount(m)) })
    end
    def fixed_count(k)
      raise ArgumentError,'k in 0..6' unless k.is_a?(Integer) && k.between?(0,N)
      den=choose(N,k)
      validate(MASKS.map { |m| popcount(m)==k ? Rational(1,den) : Rational(0) })
    end
    def popcount(mask)
      raise ArgumentError,'mask out of range' unless mask.is_a?(Integer) && mask.between?(0,(1<<N)-1)
      mask.to_s(2).count('1')
    end
    def marginal(weights,actor)
      raise ArgumentError,'actor outside 0..5' unless actor.is_a?(Integer) && actor.between?(0,N-1)
      weights.each_with_index.sum(Rational(0)) { |p,m| (m&(1<<actor)).zero? ? 0 : p }
    end
    def pair_joint(weights,actor,other)
      raise ArgumentError,'distinct actors required' if actor == other
      raise ArgumentError,'actor outside 0..5' unless [actor,other].all? { |x| x.is_a?(Integer) && x.between?(0,N-1) }
      weights.each_with_index.sum(Rational(0)) do |p,mask|
        (mask&(1<<actor))!=0 && (mask&(1<<other))!=0 ? p : 0
      end
    end
    def covariance(weights,actor,other)
      pair_joint(weights,actor,other)-marginal(weights,actor)*marginal(weights,other)
    end
  end
end
