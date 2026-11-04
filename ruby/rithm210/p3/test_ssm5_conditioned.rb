require 'minitest/autorun'
require_relative 'ssm5_conditioned'
class TestRithm210SSM5Conditioned < Minitest::Test
  M=Rithm210SSM5Conditioned
  def test_no_history_random_and_one_route_uninformed_random
    h=M.make_history
    assert_equal 0.5,M.choose_a(h,informed:true,rng:Random.new(1))
    M.add_trial(h,{'NumA'=>'4','RouteA'=>'1','profit'=>'6.0'})
    assert_equal 0.5,M.choose_a(h,informed:false,rng:Random.new(1))
  end
  def test_informed_comparison_of_counterfactual_payoffs
    h=M.make_history
    M.add_trial(h,{'NumA'=>'4','RouteA'=>'1','profit'=>'7.0'})
    assert_equal 1.0,M.choose_a(h,informed:true,rng:Random.new(1))
  end
  def test_uninformed_comparison_of_observed_route_payoffs
    h=M.make_history
    M.add_trial(h,{'NumA'=>'4','RouteA'=>'1','profit'=>'9.0'})
    M.add_trial(h,{'NumA'=>'4','RouteA'=>'0','profit'=>'4.0'})
    assert_equal 1.0,M.choose_a(h,informed:false,rng:Random.new(1))
  end
  def test_negative_payoff_difference_prefers_b
    h=M.make_history
    M.add_trial(h,{'NumA'=>'5','RouteA'=>'0','profit'=>'0.0'})
    assert_equal 0.0,M.choose_a(h,informed:true,rng:Random.new(1))
  end
end
