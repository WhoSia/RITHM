# frozen_string_literal: true
module RithmT24
  module Welfare
    module_function
    COST=(0..6).map{|n|3*(n-4)**2}.freeze
    def matrix(rows)
      p=rows.map{|r|r.map{|v|Rational(v)}}
      raise ArgumentError,'seven-state stochastic matrix' unless p.size==7 && p.all?{|r|r.size==7 && r.all?{|v|v>=0} && r.sum==1}
      p
    end
    def clock(p,scale)
      p=matrix(p);s=Rational(scale);raise ArgumentError,'scale' unless s>=0
      matrix(p.each_with_index.map{|r,i|r.each_with_index.map{|x,j|s*x+(i==j ? 1-s : 0)}})
    end
    def values(p,horizon)
      p=matrix(p);raise ArgumentError,'horizon' unless horizon.is_a?(Integer) && horizon>=1
      v=COST.dup
      (horizon-1).times{v=p.each_with_index.map{|r,i|COST[i]+r.zip(v).sum{|x,y|x*y}}}
      v
    end
    def witness
      p=Array.new(7){|i|Array.new(7){|j|i==j ? 1 : 0}}
      p[5][4]=Rational(13,200);p[5][5]=1-p[5][4]
      p[4][6]=Rational(3,1000);p[4][4]=1-p[4][6];p
    end
    # Independent cognitive gate times conditional response. All formal choices available.
    # At n=5 only old A can switch; all other states stay (deliberate counterexample).
    def cognitive(switch)
      x=Rational(switch);raise ArgumentError,'switch probability' unless x.between?(0,1)
      p=Array.new(7){|i|Array.new(7){|j|i==j ? 1 : 0}};p[5]=Array.new(7,0)
      [1,5,10,10,5,1].each_with_index{|c,m|p[5][5-m]=c*x**m*(1-x)**(5-m)}
      p
    end
    def active_gain(switch)
      x=Rational(switch);raise ArgumentError,'switch probability' unless x.between?(0,1)
      [1-12*x,-4+15*x]
    end
    # Exact Bernstein coefficients for finite horizon values over common fixed scale s.
    # Interpolate transition matrices, not separately chosen rows or time-varying nature.
    def bernstein(p,s_low,s_high,horizon,initial)
      l,h=[s_low,s_high].map{|x|Rational(x)}
      raise ArgumentError,'interval/horizon/state' unless l<=h && horizon.is_a?(Integer) && horizon>=1 && (0..6).include?(initial)
      a,b=[l,h].map{|s|clock(p,s)};v=COST.map{|c|[Rational(c)]}
      (1...horizon).each do |d|
        v=(0..6).map do |k|
          (0..d).map do |i|
            x=i<d ? Rational(d-i,d)*a[k].each_with_index.sum{|p,j|p*v[j][i]} : 0
            y=i>0 ? Rational(i,d)*b[k].each_with_index.sum{|p,j|p*v[j][i-1]} : 0
            COST[k]+x+y
          end
        end
      end
      v[initial]
    end
    def split(c)
      left=[c.first];right=[c.last]
      while c.size>1
        c=c.each_cons(2).map{|a,b|(a+b)/2};left<<c.first;right<<c.last
      end
      [left,right.reverse]
    end
    # Certified outer bounds and attained inner bounds, adaptive convex-hull subdivision.
    def envelope(c,tolerance:Rational(1,100),depth:12)
      raise ArgumentError,'bounds' unless !c.empty? && tolerance>0 && depth.is_a?(Integer) && depth>=0
      c=c.map{|v|Rational(v)};lo,hi=[c.first,c.last].minmax;stack=[[c,0]];outer_lo=nil;outer_hi=nil;leaves=0
      until stack.empty?
        z,d=stack.pop; a,b=z.minmax
        lo=[lo,z.first,z.last].min;hi=[hi,z.first,z.last].max
        if d<depth && (a<lo-tolerance || b>hi+tolerance)
          stack.concat(split(z).map{|x|[x,d+1]})
        else
          outer_lo=outer_lo ? [outer_lo,a].min : a;outer_hi=outer_hi ? [outer_hi,b].max : b;leaves+=1
        end
      end
      {outer_low:outer_lo,attained_low:lo,attained_high:hi,outer_high:outer_hi,leaves:leaves}
    end
  end
end
