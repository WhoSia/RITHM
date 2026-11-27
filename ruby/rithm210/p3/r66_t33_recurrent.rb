# frozen_string_literal: true
require_relative 'r66_t32_pair_bounds'
module RithmT33
  module Recurrent
    B=RithmT32::PairBounds; C=B::C
    COST=(0..5).map{|m|3*(1-m)**2}.freeze
    module_function
    def validate(q,r)
      raise ArgumentError,'law/recovery' unless q.size==6 && q.all?{|x|x>=0} && q.sum==1 && r.between?(0,1)
    end
    def step(q,r,v)
      [3+q.zip(v).sum{|w,x|w*x},*(1..5).map{|m|COST[m]+r*v[0]+(1-r)*v[m]}]
    end
    def finite(q,recovery,horizon)
      q=q.map{|x|Rational(x)};r=Rational(recovery);validate(q,r)
      raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon>=1
      v=COST.dup;(1...horizon).each{v=step(q,r,v)};v[0]
    end
    def bounds(p,t,recovery,horizon)
      r=Rational(recovery);raise ArgumentError,'recovery/horizon' unless r.between?(0,1) && horizon.is_a?(Integer) && horizon>=1
      vs=B.vertices(p,t,t);lo=COST.dup;hi=COST.dup
      (1...horizon).each do
        lo=step(vs.min_by{|q|q.zip(lo).sum{|w,x|w*x}},r,lo)
        hi=step(vs.max_by{|q|q.zip(hi).sum{|w,x|w*x}},r,hi)
      end
      [lo[0],hi[0]]
    end
    def stationary(q,recovery)
      q=q.map{|x|Rational(x)};r=Rational(recovery);validate(q,r)
      raise ArgumentError,'positive recovery required' unless r>0
      (3*r+q.each_with_index.sum{|w,m|m==0 ? 0 : w*COST[m]})/(r+1-q[0])
    end
    # For each admissible stationary law, compare its linear-fractional cost with baseline.
    def crossing(q,base)
      q=q.map{|x|Rational(x)};base=base.map{|x|Rational(x)};validate(q,1);validate(base,1)
      a=3-q.zip(COST).sum{|w,c|w*c};b=3-base.zip(COST).sum{|w,c|w*c}
      raise ArgumentError,'requires larger positive policy cost reduction' unless a>b && b>0
      (b*(1-q[0])-a*(1-base[0]))/(a-b)
    end
    def stationary_bounds(p,t,recovery)
      B.vertices(p,t,t).map{|q|stationary(q,recovery)}.minmax
    end
  end
end
