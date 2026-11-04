# frozen_string_literal: true
# Baseline-observation-equivalent friction models, divergent policy afterlives.
# Micro-to-macro PARTIAL IDENTIFICATION toy, not an original literature theorem.
require_relative 'adaptation_cycle'

module Rithm210PolicyWelfareEquivalence
  module_function

  def example
    x=Rational(1,2)
    rho=Rational(1,8)
    signal=Rational(2,5) # perceived one-period A cost, not a physical toll
    k_lock=Rational(1,5)
    k_cycle=0

    no_policy_lock=Rithm210FrictionWelfare.step(x:x,k:k_lock,rho:rho)
    no_policy_cycle=Rithm210FrictionWelfare.step(x:x,k:k_cycle,rho:rho)
    raise 'baseline differs' unless no_policy_lock==x && no_policy_cycle==x

    pulse_lock=Rithm210FrictionWelfare.step(x:x,k:k_lock,rho:rho,h:signal)
    pulse_cycle=Rithm210FrictionWelfare.step(x:x,k:k_cycle,rho:rho,h:signal)
    raise 'different pulse response' unless pulse_lock==pulse_cycle

    post_lock=Rithm210FrictionWelfare.step(x:pulse_lock,k:k_lock,rho:rho)
    raise 'lock-in failed' unless post_lock==pulse_lock
    cyc=Rithm210AdaptationCycle.cycle(rho:rho)
    raise 'no cycling condition' unless Rithm210AdaptationCycle.verify_step(rho:rho,kappa:k_cycle)

    # For k=0, after pulse x=7/16 lies in low-branch interval [7/16,7/15],
    # whose two-step self-map is strictly contracting with slope (1-rho)^2.
    # Each iterate alternates around 1/2 and approaches the exact two-cycle.
    low_first=pulse_cycle
    upper=cyc[:low]
    next_high=Rithm210FrictionWelfare.step(x:low_first,k:0,rho:rho)
    next_low=Rithm210FrictionWelfare.step(x:next_high,k:0,rho:rho)
    raise 'local basin not verified' unless low_first<upper &&
      next_high>Rational(1,2) && next_high<=cyc[:high] &&
      next_low>low_first && next_low<=cyc[:low]

    locked_welfare=Rithm210FrictionWelfare.excess_at_zero_bias(x:post_lock)
    cycle_welfare=cyc[:excess_cost_each_period]
    {same_no_policy_choice:no_policy_lock==no_policy_cycle,
      same_pulse_choice:pulse_lock==pulse_cycle,
      pulse_choice:pulse_lock,lock_in_state:post_lock,
      alternative_cycle_low:cyc[:low],alternative_cycle_high:cyc[:high],
      locked_long_run_excess:locked_welfare,
      cycling_long_run_excess:cycle_welfare,
      post_policy_welfare_gap:locked_welfare-cycle_welfare,
      contraction:cyc[:two_step_contraction]}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  puts JSON.pretty_generate(Rithm210PolicyWelfareEquivalence.example.transform_values(&:to_s))
end
