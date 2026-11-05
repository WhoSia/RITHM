require 'minitest/autorun'
require_relative 'r20_group_bridge'
class TestRithm210R20GroupBridge < Minitest::Test
  M=Rithm210R20GroupBridge
  def test_fair_independent_group_distribution
    p=Array.new(6,0.5)
    dist=M.convolve(p)
    assert_in_delta 1.0,dist.sum,1e-12
    assert_in_delta Rational(20,64).to_f,dist.fetch(3),1e-12
    x=M.score(p,3)
    assert_in_delta(-Math.log(20.0/64),x[:logloss],1e-12)
    assert_in_delta 3,x[:occupancy_mean],1e-12
    assert_in_delta 1.5,x[:variance],1e-12
    assert_in_delta 31.5,x[:predicted_cost],1e-12
  end
  def test_deterministic_three_a_has_zero_logloss_and_cost_27
    x=M.score([1.0,1.0,1.0,0.0,0.0,0.0],3)
    assert_in_delta 0,x[:logloss],1e-12
    assert_in_delta 0,x[:brier],1e-12
    assert_in_delta 27,x[:predicted_cost],1e-12
  end
  def test_welfare_expectation_depends_on_occupancy_variance
    # Identical mean A occupancy 3, different micro-uncertainty.
    certain=M.score([1,1,1,0,0,0],3)
    uncertain=M.score(Array.new(6,0.5),3)
    assert_in_delta 3,certain[:occupancy_mean],1e-12
    assert_in_delta 3,uncertain[:occupancy_mean],1e-12
    assert_in_delta 4.5,uncertain[:predicted_cost]-certain[:predicted_cost],1e-12
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){M.convolve(Array.new(5,0.5))}
    assert_raises(ArgumentError){M.convolve([1.1]+Array.new(5,0.5))}
    assert_raises(ArgumentError){M.score(Array.new(6,0.5),7)}
    assert_raises(ArgumentError){M.summary([])}
  end
end

class TestRithm210R20ActorMarkov < Minitest::Test
  M=Rithm210R20GroupBridge
  def test_beta_one_four_switch_prior
    assert_in_delta 0.5,M.online_markov_probability({}),1e-12
    assert_in_delta 0.8,M.online_markov_probability({count:1,previous_a:true}),1e-12
    assert_in_delta 0.2,M.online_markov_probability({count:1,previous_a:false}),1e-12
    assert_in_delta 5.0/6,M.online_markov_probability({count:2,previous_a:true,prior_a_count:1,switch_from_a:0}),1e-12
    assert_in_delta 2.0/6,M.online_markov_probability({count:2,previous_a:false,prior_b_count:1,switch_from_b:1}),1e-12
  end
  def test_impossible_switch_history_rejected
    assert_raises(RuntimeError){M.online_markov_probability({count:2,previous_a:true,prior_a_count:0,switch_from_a:1})}
  end
end
