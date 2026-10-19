# frozen_string_literal: true
require 'json'
require 'rational'
# Explicit shared-signal / level-0 congestion feedback. All quantities Rational.
# No inferred human response and no equilibrium claim: each agent forecasts
# other agents' routes fixed when estimating a unilateral move.
module RithmSharedSignal
  module_function
  def total_cost(routes, shock)
    a=routes.count(0); b=routes.size-a
    a*(a+shock)+b*b
  end
  def unilateral_gain(routes, i, shock)
    old=routes[i]
    current=routes.count(old)+(old==0 ? shock : 0)
    destination=routes.count(1-old)+1+((1-old)==0 ? shock : 0)
    current-destination
  end
  def evaluate(k:,q:,prior:Rational(1,2),initial:[0,0,1],shock_size:1)
    raise ArgumentError unless k>=0 && q>=0 && prior.between?(0,1) &&
      initial==[0,0,1] && shock_size==1
    # A-type agents can profit from moving only in world 1: gain = 1.
    # Inspection earns an expected private gain net of switching friction,
    # assuming the other agent remains fixed. A shared signal is realized
    # simultaneously, without strategic anticipation of others' inspection.
    gain_world_one = unilateral_gain(initial,0,shock_size)
    gain_world_zero = unilateral_gain(initial,0,0)
    baseline_expected_gain = (1-prior)*gain_world_zero+prior*gain_world_one
    no_inspection_switch = baseline_expected_gain>k
    inspection_value = prior*[gain_world_one-k,0].max+
      (1-prior)*[gain_world_zero-k,0].max - [baseline_expected_gain-k,0].max
    inspect = inspection_value>q
    raise ArgumentError, 'outside stable no-inspection regime' if no_inspection_switch
    outcomes=[0,shock_size].map do |z|
      routes=initial.dup
      if inspect && unilateral_gain(initial,0,z)>k
        routes[0]=1
        routes[1]=1
      end
      { 'shock'=>z,'routes'=>routes,'route_cost'=>total_cost(routes,z),
        'switching_cost'=> (routes.zip(initial).count{|a,b|a!=b})*k,
        'information_cost'=>inspect ? 2*q : 0 }
    end
    prior_cost=(1-prior)*total_cost(initial,0)+prior*total_cost(initial,shock_size)
    policy_cost=(1-prior)*outcomes[0].values_at('route_cost','switching_cost','information_cost').sum+
      prior*outcomes[1].values_at('route_cost','switching_cost','information_cost').sum
    {'inspect'=>inspect,'information_value'=>inspection_value,
      'uninspected_expected_cost'=>prior_cost,
      'inspected_expected_cost'=>policy_cost,
      'cost_delta'=>policy_cost-prior_cost,
      'outcomes'=>outcomes,'policy'=>'level-0 fixed-others conjecture; shared perfect signal',
      'strategic_equilibrium_verified'=>false,'real_data'=>false}
  end
end
if __FILE__==$PROGRAM_NAME
  a=RithmSharedSignal.evaluate(k:Rational(3,4),q:Rational(1,16))
  puts JSON.pretty_generate(a.transform_values{|x|x.is_a?(Rational) ? x.to_s : x})
end
