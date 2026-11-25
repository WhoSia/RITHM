# frozen_string_literal: true
require_relative 'r66_t24_welfare'
module RithmT24
  module Perturbation
    module_function
    # Exact extremum over a total-variation ball; optionally preserve nominal support.
    def extreme(row,v,delta,sign,support_only:false)
      p=row.map{|x|Rational(x)};d=Rational(delta)
      raise ArgumentError,'row/values/radius' unless p.size==v.size && p.all?{|x|x>=0} && p.sum==1 && d.between?(0,1) && [-1,1].include?(sign)
      ids=p.each_index.select{|i|!support_only || p[i]>0}.sort_by{|i|sign*v[i]}
      target=ids.last
      ids.each do |i|
        break if i==target || sign*v[i]>=sign*v[target] || d==0
        x=[p[i],d,1-p[target]].min;p[i]-=x;p[target]+=x;d-=x
      end
      {row:p,value:p.zip(v).sum{|a,b|a*b}}
    end
    # Rectangular row/time ambiguity: sharp for this larger uncertainty class;
    # outer bounds only for a single unknown stationary transition matrix.
    def bounds(p,horizon,delta,support_only:false)
      p=Welfare.matrix(p);d=Rational(delta)
      raise ArgumentError,'horizon/radius' unless horizon.is_a?(Integer) && horizon>=1 && d.between?(0,1)
      [-1,1].map do |s|
        v=Welfare::COST.dup
        (horizon-1).times do
          v=p.each_with_index.map{|row,i|Welfare::COST[i]+extreme(row,v,d,s,support_only:support_only)[:value]}
        end
        v
      end
    end
  end
end
