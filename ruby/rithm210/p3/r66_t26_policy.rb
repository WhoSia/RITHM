# frozen_string_literal: true
require_relative 'r66_t26_dependence'
require_relative 'r66_t24_welfare'
module RithmT26
  module Policy
    W=RithmT24::Welfare;D=Dependence
    module_function
    # Exact absorbing-state cognitive witness from T24, not general congestion dynamics.
    def weighted_sum(p,h)
      a=(1-p)**5;v=0
      (1...h).each{|i|v=i+a*v};v
    end
    def cost(p,h)
      p=Rational(p);raise ArgumentError,'probability/horizon' unless p.between?(0,1) && h.is_a?(Integer) && h>=1
      3*h+3*p*(20*p-5)*weighted_sum(p,h)
    end
    def cost_range(l,u,h)
      l,u=[l,u].map{|x|Rational(x)}
      raise ArgumentError,'interval/horizon' unless 0<=l && l<=u && u<=1 && h.is_a?(Integer) && h>=1
      f=D.range([0,-15,60],l,u);g=[weighted_sum(u,h),weighted_sum(l,h)]
      f.product(g).map{|a,b|3*h+a*b}.minmax
    end
    # Certify improvement over a union of outer q intervals, including unresolved boundaries.
    def certify(s,intervals,horizon:40,depth:16)
      s=Rational(s);base=cost(s,horizon);stack=intervals.map{|l,u,_|[Rational(l),Rational(u),0]}
      raise ArgumentError,'q intervals' unless s>0 && stack.all?{|l,u,_|s<=l && l<=u && u<=1} && depth.is_a?(Integer) && depth>=0
      out=[]
      until stack.empty?
        l,u,d=stack.pop;lo,hi=cost_range(s/u,s/l,horizon)
        status=hi<base ? :improves : lo>base ? :worsens : :unresolved
        if status==:unresolved && d<depth && l<u
          m=(l+u)/2;stack<<[m,u,d+1]<<[l,m,d+1]
        else
          out<<[l,u,status,lo,hi]
        end
      end
      {baseline:base,intervals:out,improvement_certified:!out.empty? && out.all?{|x|x[2]==:improves}}
    end
    # q' = min(m*q,1), so post-policy switch probability is s/max(q,1/m).
    def relative(s,intervals,multiplier:,horizon:40,depth:16)
      m=Rational(multiplier);raise ArgumentError,'multiplier' unless m>=1
      effective=intervals.map{|l,u,status|[[Rational(l),1/m].max,[Rational(u),1/m].max,status]}
      certify(s,effective,horizon:horizon,depth:depth)
    end
  end
end
