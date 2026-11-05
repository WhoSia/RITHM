# frozen_string_literal: true
# Exact atomic route-choice game. A stale snapshot of all opponents' current actions
# is assumed; this is NOT available to all actors in the actual laboratory information sets.
require_relative 'atomic_nash_potential'
module Rithm210AdjustmentClocks
  module_function
  G=Rithm210AtomicNash
  def synchronous(n)
    G.group_cost(n)
    a_stay = (n==0 || G.a_to_b_cost_change(n)>=0) ? n : 0
    b_move = (n==6 || G.b_to_a_cost_change(n)>=0) ? 0 : 6-n
    a_stay+b_move
  end
  def asynchronous(n,who:) # who is :a or :b, one player selected
    G.group_cost(n)
    case who
    when :a
      raise ArgumentError,'no A user' if n==0
      G.a_to_b_cost_change(n)<0 ? n-1 : n
    when :b
      raise ArgumentError,'no B user' if n==6
      G.b_to_a_cost_change(n)<0 ? n+1 : n
    else
      raise ArgumentError,'unknown agent route'
    end
  end
  def expected_async_hitting_time(n)
    G.group_cost(n)
    if n<4
      (n...4).sum{|k|6.0/(6-k)}
    elsif n>4
      (5..n).sum{|k|6.0/k}
    else
      0.0
    end
  end
  def synchronous_attractor(n)
    G.group_cost(n)
    n==4 ? [4] : [0,6]
  end
  def audit
    map=(0..6).to_h{|n|[n,synchronous(n)]}
    raise 'unexpected synchronous rule' unless map=={0=>6,1=>6,2=>6,3=>6,4=>4,5=>0,6=>0}
    stationary_cycle_cost=(G.group_cost(0)+G.group_cost(6))/2.0
    {synchronous:map,unique_nash_occupancy:4,
     two_cycle_occupancies:[0,6],
     two_cycle_mean_group_congestion:stationary_cycle_cost,
     efficient_group_congestion:G.group_cost(4),
     cycle_mean_excess:stationary_cycle_cost-G.group_cost(4),
     one_agent_expected_hitting_times:(0..6).to_h{|n|[n,expected_async_hitting_time(n)]}}
  end
end
