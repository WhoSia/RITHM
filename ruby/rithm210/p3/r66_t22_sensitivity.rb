# frozen_string_literal: true
require_relative 'r66_t22_identification'
module RithmT22
  module Sensitivity
    I=Identification
    module_function
    # Allow outcome-dependent proxy error. Only the average sensitivity among
    # active movers vs active nonmovers differs by at most delta. No restriction
    # on the tag distribution across distinct changed states, or inactive beta.
    def bounds(k,j0,j1,route,delta:)
      I.check_state(k);a,b=[j0,j1].map{|v|v.map{|x|Rational(x)}};d=Rational(delta)
      raise ArgumentError,'joint rows/delta' unless [a,b].all?{|v|v.size==6 && v.all?{|x|x>=0}} && a.sum+b.sum==1 && d.between?(0,1)
      p=a.zip(b).map(&:sum);r=1-p[k];s=b[k]
      raise ArgumentError,'no observed changes' if r==0
      alpha=(b.sum-s)/r;lo=[0,alpha-d].max;hi=[1,alpha+d].min
      qh=Rational(1);qh=[qh,r+s/lo].min if lo>0;qh=[qh,r+(1-r-s)/(1-hi)].min if hi<1
      I.bounds(k,p,route,q_min:r,q_max:qh).merge(alpha_mover:alpha,alpha_nonmover_low:lo,alpha_nonmover_high:hi)
    end
    # Construct a feasible joint decomposition for any q in the sharp region.
    # Returns active tagged/untagged joint masses and inactive tagged/untagged mass.
    def witness(k,j0,j1,q,delta:)
      a,b=[j0,j1].map{|v|v.map{|x|Rational(x)}};q=Rational(q)
      x=bounds(k,a,b,:a,delta:delta);raise ArgumentError,'q infeasible' unless q.between?(x[:q_low],x[:q_high])
      r=1-a[k]-b[k];active_stay=q-r;inactive=1-q
      tagged_active_stay=[x[:alpha_nonmover_low]*active_stay,b[k]-inactive].max
      raise 'feasibility' unless tagged_active_stay<=[x[:alpha_nonmover_high]*active_stay,b[k]].min
      tagged_active=b.dup;untagged_active=a.dup
      tagged_active[k]=tagged_active_stay;untagged_active[k]=active_stay-tagged_active_stay
      {active_tagged:tagged_active,active_untagged:untagged_active,inactive_tagged:b[k]-tagged_active_stay,inactive_untagged:a[k]-untagged_active[k]}
    end
  end
end
