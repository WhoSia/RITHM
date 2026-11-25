# frozen_string_literal: true
# R66-T22: common revision opportunity, no movement when inactive.
module RithmT22
  module Identification
    module_function
    def distribution(row)
      p=row.map { |x| Rational(x) }
      raise ArgumentError,'six-state probability row' unless p.size==6 && p.all? { |x| x>=0 } && p.sum==1
      p
    end
    def check_state(k)
      raise ArgumentError,'state' unless k.is_a?(Integer) && k.between?(0,5)
    end
    def mix(k,active,q)
      check_state(k); a=distribution(active); q=Rational(q)
      raise ArgumentError,'q' unless q.between?(0,1)
      a.each_with_index.map { |v,j| q*v+(j==k ? 1-q : 0) }
    end
    def recover(k,pooled,q)
      check_state(k); p=distribution(pooled); q=Rational(q)
      raise ArgumentError,'infeasible or unidentified q' unless q>0 && q<=1 && q>=1-p[k]
      p.each_with_index.map { |v,j| (v-(j==k ? 1-q : 0))/q }
    end
    def gain(row,route)
      raise ArgumentError,'route' unless [:a,:b].include?(route)
      distribution(row).each_with_index.sum { |p,j| p*(3*j-11) }*(route==:a ? 1 : -1)
    end
    # q unknown but strictly positive. If P=identity, all compatible active rows are identity.
    def bounds(k,pooled,route,q_min:0,q_max:1)
      check_state(k); p=distribution(pooled); l,h=[q_min,q_max].map { |x| Rational(x) }
      raise ArgumentError,'q bounds' unless 0<=l && l<=h && h<=1 && h>0
      l=[l,1-p[k]].max
      raise ArgumentError,'empty feasible set' if l>h
      if p[k]==1
        g=gain(p,route);return {low:g,high:g,q_low:l,q_high:h}
      end
      gs=[l,h].map { |q| gain(recover(k,p,q),route) }
      {low:gs.min,high:gs.max,q_low:l,q_high:h}
    end
  end
end
