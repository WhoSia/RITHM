# frozen_string_literal: true
require_relative 'r66_t22_identification'
module RithmT22
  module Proxy
    I=Identification
    module_function
    # Joint rows J_z(j)=P(K_next=j,Z=z|K_current=k).
    # Z is a binary proxy, independent of next state conditional on true opportunity E.
    # Inactive implies identity. q>0. When changes occur, sensitivity is identified.
    def bounds(k,j0,j1,route,false_positive:nil)
      I.check_state(k);a,b=[j0,j1].map{|r|r.map{|x|Rational(x)}}
      raise ArgumentError,'joint rows' unless [a,b].all?{|r|r.size==6 && r.all?{|v|v>=0}} && a.sum+b.sum==1
      p=a.zip(b).map(&:sum);r=1-p[k];m=b.sum
      raise ArgumentError,'no changed observations' if r==0
      alpha=(m-b[k])/r
      (0..5).each do |j|
        next if j==k
        raise ArgumentError,'nondifferential proxy rejected' unless b[j]==alpha*p[j]
      end
      l=r;h=Rational(1);h=[h,m/alpha].min if alpha>0;h=[h,(1-m)/(1-alpha)].min if alpha<1
      if !false_positive.nil?
        beta=Rational(false_positive);raise ArgumentError,'beta' unless beta.between?(0,1)
        if beta==alpha
          raise ArgumentError,'incompatible beta' unless m==alpha
        else
          q=(m-beta)/(alpha-beta);l=[l,q].max;h=[h,q].min
        end
      end
      raise ArgumentError,'incompatible proxy' if l>h
      I.bounds(k,p,route,q_min:l,q_max:h).merge(sensitivity:alpha,tag_rate:m)
    end
    def joint(k,active,q,alpha,beta)
      I.check_state(k);a=I.distribution(active);q,alpha,beta=[q,alpha,beta].map{|v|Rational(v)}
      raise ArgumentError,'probabilities' unless [q,alpha,beta].all?{|v|v.between?(0,1)}
      [1-alpha,alpha].each_with_index.map do |sens,z|
        a.each_with_index.map{|v,j|q*sens*v+(j==k ? (1-q)*(z==0 ? 1-beta : beta) : 0)}
      end
    end
  end
end
