require 'minitest/autorun'
require_relative 'policy_welfare_equivalence'
class TestRithm210PolicyWelfareEquivalence < Minitest::Test
  M=Rithm210PolicyWelfareEquivalence
  def test_same_observed_baseline_and_first_signal_response
    x=M.example
    assert x[:same_no_policy_choice]
    assert x[:same_pulse_choice]
    assert_equal Rational(7,16),x[:pulse_choice]
  end
  def test_divergent_long_run_welfare_after_signal_removed
    x=M.example
    assert_equal Rational(1,128),x[:locked_long_run_excess]
    assert_equal Rational(1,450),x[:cycling_long_run_excess]
    assert_equal Rational(161,28800),x[:post_policy_welfare_gap]
    assert_operator x[:post_policy_welfare_gap],:>,0
  end
  def test_cycle_and_local_stability
    x=M.example
    assert_equal Rational(7,15),x[:alternative_cycle_low]
    assert_equal Rational(8,15),x[:alternative_cycle_high]
    assert_equal Rational(49,64),x[:contraction]
  end
end
