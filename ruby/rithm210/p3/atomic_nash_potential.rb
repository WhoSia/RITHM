# frozen_string_literal: true
# Six-person atomic congestion game: exact potential, Nash configurations and social optimum.
module Rithm210AtomicNash
  module_function
  def group_cost(n)
    raise ArgumentError,'outside six-player occupancy' unless n.is_a?(Integer) && n.between?(0,6)
    n*n+2*(6-n)**2
  end
  def potential(n)
    group_cost(n) # validates
    n*(n+1)/2+(6-n)*(7-n)
  end
  def b_to_a_cost_change(n)
    raise ArgumentError,'no B agents' unless n.is_a?(Integer) && n.between?(0,5)
    (n+1)-2*(6-n)
  end
  def a_to_b_cost_change(n)
    raise ArgumentError,'no A agents' unless n.is_a?(Integer) && n.between?(1,6)
    2*(7-n)-n
  end
  def nash_occupancy?(n)
    group_cost(n)
    (n==0 || a_to_b_cost_change(n)>=0) &&
      (n==6 || b_to_a_cost_change(n)>=0)
  end
  def equilibrium_summary
    occupancies=(0..6).select{|n|nash_occupancy?(n)}
    efficient=(0..6).select{|n|group_cost(n)==(0..6).map{|m|group_cost(m)}.min}
    raise 'unique occupancy mismatch' unless occupancies==[4] && efficient==[4]
    {nash_occupancies:occupancies,socially_optimal_occupancies:efficient,
      number_of_pure_nash_action_profiles:15,
      a_to_b_loss_at_n4:a_to_b_cost_change(4),
      b_to_a_loss_at_n4:b_to_a_cost_change(4),
      group_optimum_cost:group_cost(4),potential_at_optimum:potential(4)}
  end
end
