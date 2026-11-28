# frozen_string_literal: true
require 'json'
require_relative 'r66_t33_recurrent'
module RithmT38
  module Fiber
    R=RithmT33::Recurrent
    P=7r/160; REC=1r/100; H=40
    module_function
    def mix(a,b,w)
      a.zip(b).map{|x,y|x+(y-x)*w}
    end
    def event(q,indices)
      indices.sum{|i|q.fetch(i)}
    end
    # Slice the convex hull at one measured scalar; vertices of the slice
    # lie on original vertices or edges (all vertex pairs suffice).
    def slice(vs,indices,z)
      out=vs.select{|q|event(q,indices)==z}
      vs.combination(2) do |a,b|
        x=event(a,indices);y=event(b,indices)
        out<<mix(a,b,(z-x)/(y-x)) if x!=y && z.between?(*[x,y].minmax)
      end
      raise ArgumentError,'empty measurement fiber' if out.empty?
      out.minmax_by(&:first)
    end
    # q0 alone determines cost on this fixed moment fiber.
    # For q0>=r, all nonconstant coefficients of -cost in q0-r are nonnegative.
    def cost_and_slope(q0,mean_cost,r,h)
      raise ArgumentError,'domain' unless r.between?(0,q0) && q0<=1 && mean_cost<3 && h.is_a?(Integer) && h>=1
      a=3-mean_cost;s=1;ds=0;d=0;dd=0;j=3;dj=0
      (h-1).times do
        d=(1-r)*d-a*s;dd=(1-r)*dd-a*ds
        j+=3+d;dj+=dd
        ds=s+(q0-r)*ds;s=r+(q0-r)*s
      end
      [j,-dj]
    end
    def harm_floor(a,b)
      raise ArgumentError,'opposing losses' unless a>0 && b>0
      a*b/(a+b)
    end
    def setup
      vs=R::B.vertices(P,P*P,P*P).map{|q|q.map{|x|Rational(x)}}
      low,high=vs.minmax_by(&:first);m=low.zip(R::COST).sum{|x,y|x*y}
      base=R.finite(R::C.independent([7r/200]*5),REC,H)
      f=lambda{|q|cost_and_slope(q,m,REC,H).first-base}
      l=low.first;u=high.first;raise 'no crossing' unless f.call(l)>0 && f.call(u)<0
      48.times do
        z=(l+u)/2;f.call(z)>0 ? l=z : u=z
      end
      # Interior barycenter moved toward the relevant endpoint to reach the root bracket.
      mid=(l+u)/2;center=low.each_index.map{|i|vs.sum{|q|q[i]}/vs.size}
      edge=mid>center.first ? high : low
      interior= center.first==mid ? center : mix(center,edge,(mid-center.first)/(edge.first-center.first))
      {vertices:vs,mean_cost:m,baseline:base,bracket:[l,u],interior:interior,slope:cost_and_slope(high.first,m,REC,H).last}
    end
    def witness(set,indices,z)
      low,high=slice(set[:vertices],indices,z);a=set[:baseline]-cost_and_slope(high.first,set[:mean_cost],REC,H).first
      b=cost_and_slope(low.first,set[:mean_cost],REC,H).first-set[:baseline]
      {low:high,high:low,improvement:a,harm:b,floor:(a>0 && b>0 ? harm_floor(a,b) : 0r)}
    end
    def audit
      s=setup;z=11r/1000;w=witness(s,[2,3,4,5],z)
      events=(1...32).map do |mask|
        idx=(0..5).select{|i|mask[i]==1};prob=event(s[:interior],idx);v=witness(s,idx,prob)
        {indices:idx,probability:prob.to_f,alias_floor:v[:floor].to_f}
      end
      # e>2 yields a conservative exact sufficient sample size for Hoeffding bound.
      n=(s[:slope]**2/(8*w[:floor]**2)).floor+1
      {synthetic_only:true,reference:'T33 reset model, full exchangeable moment fiber, stationary laws, iid event observations',q0_crossing:s[:bracket].map(&:to_f),slope_bound:s[:slope].to_f,
       witness:{event_probability:z.to_s,low:w[:low].map(&:to_s),high:w[:high].map(&:to_s),improvement:w[:improvement].to_f,harm:w[:harm].to_f,regret_floor:w[:floor].to_f},
       all_binary_events_up_to_complement:events,conservative_sample_size_for_no_switch_bound:n,hoeffding_upper_at_n:s[:slope].to_f/(2*Math.sqrt(Math::E*n))}
    end
  end
end
puts JSON.pretty_generate(RithmT38::Fiber.audit) if $PROGRAM_NAME==__FILE__
