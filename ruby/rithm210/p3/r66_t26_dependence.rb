# frozen_string_literal: true
require_relative 'r66_t25_two_proxy'
module RithmT26
  module Dependence
    T=RithmT25::TwoProxy
    module_function
    def range(c,l,h)
      a,b,d=c.map{|x|Rational(x)};xs=[l,h];v=-b/(2*d) unless d==0
      xs<<v if v && v.between?(l,h)
      xs.map{|q|a+b*q+d*q*q}.minmax
    end
    def constraints(j0,j1,delta)
      s,r,a=T.observed(j0,j1);d=Rational(delta)
      raise ArgumentError,'covariance radius' unless d.between?(0,Rational(1,4))
      h=[1,a.each_index.filter_map{|i|r[i]/a[i] if a[i]>0}.min].min
      cross=r[0]*a[3]+r[3]*a[0]-r[1]*a[2]-r[2]*a[1]
      cs=[-1,1].map{|sign|[sign*T.det(r)-d,-sign*cross+2*d,sign*T.det(a)-d]}
      [s,h,cs]
    end
    # Exact sign classification; unresolved boundary intervals are an outer cover.
    def cover(j0,j1,delta:,width:Rational(1,100_000))
      w=Rational(width);raise ArgumentError,'width' unless w>0
      l,h,cs=constraints(j0,j1,delta);stack=[[l,h]];out=[]
      until stack.empty?
        a,b=stack.pop;rs=cs.map{|c|range(c,a,b)}
        next if rs.any?{|lo,_|lo>0}
        if rs.all?{|_,hi|hi<=0}
          out<<[a,b,:inside]
        elsif b-a<=w
          out<<[a,b,:boundary]
        else
          m=(a+b)/2;stack<<[m,b]<<[a,m]
        end
      end
      out.each_with_object([]) do |(a,b,s),merged|
        if merged.last && merged.last[1]==a && merged.last[2]==s
          merged.last[1]=b
        else
          merged<<[a,b,s]
        end
      end
    end
    def feasible?(j0,j1,q,delta:)
      l,h,cs=constraints(j0,j1,delta);q=Rational(q)
      q.between?(l,h) && cs.all?{|c|range(c,q,q).last<=0}
    end
  end
end
