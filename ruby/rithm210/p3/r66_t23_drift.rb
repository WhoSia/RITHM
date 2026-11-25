# frozen_string_literal: true
require_relative 'r66_t22_identification'
module RithmT23
  module Drift
    I=RithmT22::Identification
    module_function
    # P=q*A+(1-q)*B; B(off diagonal)<=eps. q strictly positive.
    def minimum_q(k,row,eps)
      I.check_state(k);p=I.distribution(row);e=Rational(eps)
      raise ArgumentError,'drift' unless e.between?(0,1)
      e==1 ? 0 : [0,(1-p[k]-e)/(1-e)].max
    end
    def shared_minimum(rows,eps)
      raise ArgumentError,'six rows' unless rows.size==6
      rows.each_with_index.map { |p,k| minimum_q(k,p,eps) }.max
    end
    def at(k,p,t,e,route,sign)
      r=1-p[k];lo=[0,1-p[k]*t,e+(r-e)*t].max;hi=[1,r*t].min
      return nil if lo>hi
      weights=(0..5).map { |j| (3*j-11)*(route==:a ? 1 : -1) }
      order=(0..5).reject { |j| j==k }.sort_by { |j| -sign*(weights[j]-weights[k]) }
      desirable=order.select { |j| sign*(weights[j]-weights[k])>0 }.sum { |j| p[j]*t }
      remaining=[[desirable,lo].max,hi].min
      a=Array.new(6,0);order.each { |j| a[j]=[remaining,p[j]*t].min;remaining-=a[j] }
      a[k]=1-a.sum;raise 'allocation' unless remaining==0
      q=1/t;b=q==1 ? Array.new(6){|j| j==k ? 1 : 0} : p.zip(a).map { |x,y| (x-q*y)/(1-q) }
      {gain:I.gain(a,route),q:q,active:a,inactive:b}
    end
    # All allocation regimes are affine in t=1/q. Include their breakpoints.
    def bounds(k,row,route,eps:,q_min:,q_max:1)
      I.check_state(k);p=I.distribution(row);e,l,h=[eps,q_min,q_max].map{|v|Rational(v)}
      raise ArgumentError,'parameters' unless [:a,:b].include?(route) && e.between?(0,1) && 0<l && l<=h && h<=1
      l=[l,minimum_q(k,p,e)].max;raise ArgumentError,'empty feasible set' if l>h
      tl,th=1/h,1/l;r=1-p[k]
      # line is intercept,slope; cumulative caps for both greedy orders.
      lines=[[0,0],[1,-p[k]],[e,r-e],[1,0],[0,r]]
      [-1,1].each do |s|
        order=(0..5).reject{|j|j==k}.sort_by{|j|s*j};z=0
        order.each{|j|z+=p[j];lines<<[0,z]}
      end
      ts=[tl,th];lines.uniq.combination(2) do |(a,b),(c,d)|
        next if b==d
        t=Rational(c-a,b-d);ts<<t if t.between?(tl,th)
      end
      ts.uniq!
      lo=ts.filter_map{|t|at(k,p,t,e,route,-1)}.min_by{|x|x[:gain]}
      hi=ts.filter_map{|t|at(k,p,t,e,route,1)}.max_by{|x|x[:gain]}
      raise 'no feasible vertex' unless lo && hi
      {low:lo,high:hi,q_low:l,q_high:h,vertices:ts.size}
    end
  end
end
