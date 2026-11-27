# frozen_string_literal: true
module RithmT35
  module Span
    module_function
    def dot(a,b)
      a.zip(b).sum{|x,y|x*y}
    end
    def apply(p,v)
      p.map{|r|dot(r,v)}
    end
    def rank(rows)
      return 0 if rows.empty?
      n=rows.first.size;raise ArgumentError,'ragged matrix' unless rows.all?{|r|r.size==n}
      a=rows.map{|r|r.map{|x|Rational(x)}};k=0
      n.times do |j|
        i=(k...a.size).find{|l|a[l][j]!=0};next unless i
        a[i],a[k]=a[k],a[i];d=a[k][j];a[k].map!{|v|v/d}
        (k+1...a.size).each{|l|d=a[l][j];a[l]=a[l].zip(a[k]).map{|x,y|x-d*y} if d!=0}
        k+=1;break if k==a.size
      end;k
    end
    def validate(p,c)
      n=c.size;raise ArgumentError,'transition dimensions' unless n>0 && p.size==n && p.all?{|r|r.size==n && r.all?{|x|x>=0} && r.sum==1}
    end
    # Include constants, since probability rows always have mass one.
    def basis(p,c)
      validate(p,c);b=[Array.new(c.size,1)];v=c.map{|x|Rational(x)}
      c.size.times do
        break if rank(b+[v])==b.size
        b<<v;v=apply(p,v)
      end;b
    end
    def equivalent?(p,q,c)
      validate(q,c);basis(p,c).all?{|v|apply(p,v)==apply(q,v)}
    end
    # Number of independent extra unrestricted linear measurements, assuming the
    # feasible row has relative interior in the affine space defined by observed.
    def deficit(observed,targets)
      rank(observed+targets)-rank(observed)
    end
    def additions(observed,targets)
      b=observed.dup;out=[];targets.each do |v|
        if rank(b+[v])>rank(b);b<<v;out<<v;end
      end;out
    end
    def values(p,c,h)
      validate(p,c);raise ArgumentError,'horizon' unless h.is_a?(Integer)&&h>=1
      v=c;(1...h).each{v=c.zip(apply(p,v)).map{|x,y|x+y}};v
    end
    def rectangular(models,c,h)
      models.each{|p|validate(p,c)};raise ArgumentError,'models/horizon' unless !models.empty?&&h.is_a?(Integer)&&h>=1
      lo=hi=c;(1...h).each do
        a=models.map{|p|apply(p,lo)};b=models.map{|p|apply(p,hi)}
        lo=c.each_with_index.map{|v,i|v+a.map{|x|x[i]}.min};hi=c.each_with_index.map{|v,i|v+b.map{|x|x[i]}.max}
      end;[lo,hi]
    end
  end
end
