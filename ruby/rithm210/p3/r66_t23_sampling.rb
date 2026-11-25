# frozen_string_literal: true
require_relative 'r66_t22_identification'
module RithmT23
  module Sampling
    module_function
    # Simultaneous Hoeffding region for independent conditional-row draws.
    # Not a serial-transition or clustered-human-data confidence procedure.
    def bounds(k,counts,route,eps:,q_min:,q_max:1,alpha:0.05)
      RithmT22::Identification.check_state(k)
      raise ArgumentError,'counts/route' unless counts.size==6 && counts.all?{|x|x.is_a?(Integer) && x>=0} && counts.sum>0 && [:a,:b].include?(route)
      e,l,h,a=[eps,q_min,q_max,alpha].map(&:to_f)
      raise ArgumentError,'parameters' unless e.between?(0,1) && l.between?(0,1) && l<=h && h.between?(0,1) && h>0 && a>0 && a<1
      n=counts.sum;w=(0..5).map{|j|(3*j-11)*(route==:a ? 1 : -1)};gk=w[k]
      z=Math.sqrt(Math.log(4/a)/(2*n));r=1-counts[k].to_f/n;mean=counts.zip(w).sum{|c,g|c*g}.to_f/n
      rlo=[0,r-z].max;rhi=[1,r+z].min;glo=[w.min,mean-15*z].max;ghi=[w.max,mean+15*z].min
      l=[l,(rlo-e)/(1-e)].max if e<1
      return {status: :incompatible,confidence:1-a} if l>h
      base={status: :ok,confidence:1-a,n:n,q_low:l,q_high:h,r:[rlo,rhi],pooled_gain:[glo,ghi]}
      # q can approach zero, so avoid unstable division; vacuous valid range.
      return base.merge(low:w.min,high:w.max) if l<=0
      blo=(1-e)*gk+e*w.min;bhi=(1-e)*gk+e*w.max
      low=[l,h].map{|q|(glo-(1-q)*bhi)/q}.min
      high=[l,h].map{|q|(ghi-(1-q)*blo)/q}.max
      base.merge(low:[w.min,low].max,high:[w.max,high].min)
    end
  end
end
