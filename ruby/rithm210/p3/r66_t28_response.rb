# frozen_string_literal: true
require_relative 'r66_t26_policy'
module RithmT28
  module Response
    P=RithmT26::Policy
    module_function
    # Gate saturates at one; conditional response is multiplied then capped at one.
    def switch(s,q,m,eta)
      [m*q,1].min*[eta*s/q,1].min
    end
    def bounds(s,q_low,q_high,m,delta)
      s,l,h,m,d=[s,q_low,q_high,m,delta].map{|x|Rational(x)}
      raise ArgumentError,'parameters' unless 0<s && s<=l && l<=h && h<=1 && m>=1 && d.between?(0,1)
      peak=[[1/m,l].max,h].min
      low=[l,h].map{|q|[switch(s,q,m,1-d),q,1-d]}.min_by(&:first)
      high=[switch(s,peak,m,1+d),peak,1+d]
      [low,high]
    end
    # Exact outer cost certificates; an attained endpoint can refute improvement.
    def certify(s,q_low,q_high,m,delta,horizon:40,depth:18)
      raise ArgumentError,'depth' unless depth.is_a?(Integer) && depth>=0
      lo,hi=bounds(s,q_low,q_high,m,delta);base=P.cost(s,horizon)
      [lo,hi].each do |w|
        v=P.cost(w.first,horizon)
        return {status: :not_strict,witness:w,cost:v,baseline:base} if v>=base
      end
      stack=[[lo.first,hi.first,0]];outer=nil
      until stack.empty?
        a,b,k=stack.pop;_,u=P.cost_range(a,b,horizon)
        if u<base
          outer=outer ? [outer,u].max : u
        elsif k>=depth || a==b
          return {status: :unresolved,baseline:base}
        else
          mid=(a+b)/2;stack<<[a,mid,k+1]<<[mid,b,k+1]
        end
      end
      {status: :improves,upper_cost:outer,baseline:base,switch_interval:[lo.first,hi.first]}
    end
  end
end
