# frozen_string_literal: true
module RithmT31
  module Coupling
    module_function
    def marginals(ps)
      raise ArgumentError,'probabilities' unless !ps.empty? && ps.size<=6 && ps.all?{|p|p.finite? && p.between?(0,1)}
      ps.map{|p|Rational(p)}
    end
    # Common uniform threshold maximizes every pairwise intersection.
    def upper(ps)
      p=marginals(ps); partition([0,1,*p]){|u|p.map{|x|u<x ? 1 : 0}}
    end
    # Systematic rounding on a unit circle preserves each marginal and rounds the total.
    def lower(ps)
      p=marginals(ps);edges=[0];p.each{|x|edges<<edges.last+x}
      partition([0,1,*edges.map{|x|x%1}]) do |u|
        edges.each_cons(2).map{|a,b|(b-u).ceil-(a-u).ceil}
      end
    end
    def partition(edges)
      law=Hash.new(0)
      edges.uniq.sort.each_cons(2){|a,b|law[yield((a+b)/2)]+=b-a if b>a}
      law
    end
    def occupancy(law,n)
      q=Array.new(n+1,0);law.each{|bits,w|q[bits.sum]+=w};q
    end
    def bounds(ps,target:4)
      p=marginals(ps);m=p.sum;f=m%1
      lo=3*((m-target)**2+f*(1-f))
      hi=3*(target**2+(1-2*target)*m+2*p.combination(2).sum{|a,b|[a,b].min})
      [lo,hi]
    end
    # Exact absorbing n=5 witness. M = number of old-A switches, old B stays.
    def absorbing_cost(q,horizon)
      raise ArgumentError,'switch law/horizon' unless q.size==6 && q.all?{|x|x>=0} && q.sum==1 && horizon.is_a?(Integer) && horizon>=1
      a=q.each_with_index.sum{|w,m|m==0 ? 0 : w*3*(1-m)**2};v=3
      (1...horizon).each{|t|v=3+q[0]*v+t*a};v
    end
    def independent(ps)
      marginals(ps).reduce([1]) do |q,p|
        z=Array.new(q.size+1,0);q.each_with_index{|w,i|z[i]+=w*(1-p);z[i+1]+=w*p};z
      end
    end
  end
end
