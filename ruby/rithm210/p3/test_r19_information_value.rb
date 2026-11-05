require 'minitest/autorun'
require_relative 'r19_information_value'
class TestRithm210R19InformationValue < Minitest::Test
  M=Rithm210R19InformationValue
  def test_conditional_costs_and_cutoff
    c=M.actor0_costs
    assert_equal 1260,c[:a]
    assert_equal 1020,c[:b]
    assert_equal 1080,c[:baseline]
    assert_equal 1080,M.expected_intervention_cost(prob_actor0_a:1.to_r/4)
  end
  def test_90_percent_signal_changes_policy
    a=M.decision_given_signal(signal: :a,accuracy:9.to_r/10)
    b=M.decision_given_signal(signal: :b,accuracy:9.to_r/10)
    assert_equal 9.to_r/10,a[:posterior_a]
    assert_equal 1.to_r/10,b[:posterior_a]
    refute a[:choose_treatment]
    assert b[:choose_treatment]
    assert_equal 1044,b[:treat_cost]
    assert_equal 18,M.ex_ante_value(accuracy:9.to_r/10)[:information_value]
  end
  def test_threshold_and_full_information
    assert_equal 0,M.ex_ante_value(accuracy:3.to_r/4)[:information_value]
    assert_equal 30,M.ex_ante_value(accuracy:1.to_r)[:information_value]
    assert_equal 0,M.ex_ante_value(accuracy:1.to_r/2)[:information_value]
  end
  def test_information_monotonicity
    a=(5..10).map{|v|M.ex_ante_value(accuracy:v.to_r/10)[:information_value]}
    assert_equal a.sort,a
  end
  def test_invalid_inputs
    assert_raises(ArgumentError){M.posterior_prob_a(signal: :other,accuracy:9.to_r/10)}
    assert_raises(ArgumentError){M.posterior_prob_a(signal: :a,accuracy:1.to_r,prior:0.to_r)}
    assert_raises(ArgumentError){M.ex_ante_value(accuracy:2.to_r/5)}
  end
end
