# frozen_string_literal: true
# General-N exact atomic congestion example, all agents best-respond to the same stale snapshot.
# Costs: A users each pay n; B users each pay 2*(N-n).
# This is a reference theorem, not a novelty claim or the original human information set.
module Rithm210GeneralAdjustmentClocks
  module_function
  def validate(n,total:)
    raise ArgumentError,'invalid population or occupancy' unless
      total.is_a?(Integer) && total>=3 &&
      n.is_a?(Integer) && n.between?(0,total)
  end
  def cost(n,total:)
    validate(n,total:total)
    n*n+2*(total-n)**2
  end
  def b_to_a_change(n,total:)
    validate(n,total:total)
    raise ArgumentError,'no B actor' if n==total
    n+1-2*(total-n)
  end
  def a_to_b_change(n,total:)
    validate(n,total:total)
    raise ArgumentError,'no A actor' if n==0
    2*(total-n+1)-n
  end
  def potential(n,total:)
    validate(n,total:total)
    n*(n+1)/2+(total-n)*(total-n+1)
  end
  def synchronous(n,total:)
    validate(n,total:total)
    keep_a=(n==0 || a_to_b_change(n,total:total)>=0) ? n : 0
    add_b=(n==total || b_to_a_change(n,total:total)>=0) ? 0 : total-n
    keep_a+add_b
  end
  def nash_states(total:)
    raise ArgumentError,'population' unless total.is_a?(Integer) && total>=3
    (0..total).select do |n|
      (n==0 || a_to_b_change(n,total:total)>=0) &&
      (n==total || b_to_a_change(n,total:total)>=0)
    end
  end
  def optimal_states(total:)
    values=(0..total).to_h{|n|[n,cost(n,total:total)]}
    minimum=values.values.min
    values.keys.select{|n|values[n]==minimum}
  end
  def theorem_divisible_by_three(total:)
    raise ArgumentError,'N>=3 multiple of 3' unless total.is_a?(Integer) && total>=3 && total%3==0
    n=2*total/3
    raise 'unique Nash and efficient state' unless nash_states(total:total)==[n] &&
      optimal_states(total:total)==[n]
    raise 'extreme two-cycle' unless synchronous(0,total:total)==total &&
      synchronous(total,total:total)==0
    cycle=Rational(cost(0,total:total)+cost(total,total:total),2)
    best=cost(n,total:total)
    {total:total,nash:n,efficient:n,cycle:[0,total],
      cycle_mean_cost:cycle,optimal_cost:best,
      dynamic_excess:cycle-best,
      ratio:cycle/Rational(best),
      asserted_closed_form_excess:Rational(5*total*total,6)}
  end
end
