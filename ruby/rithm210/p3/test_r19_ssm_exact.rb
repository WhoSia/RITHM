require 'minitest/autorun'
require_relative 'r19_ssm_exact'
class TestRithm210R19SSMExact < Minitest::Test
  M=Rithm210R19SSMExact
  def test_uninformed_filtration
    h=M.blank_history
    M.append(history:h,route_a:true,informed:false,payoff_tenths:97,num_a:Object.new)
    assert_equal [],h[:paired_differences]
    assert_equal [97],h[:payoffs_a]
    assert_equal Rational(1,2),M.probability(history:h,q:5,informed:false)
    assert_raises(ArgumentError){M.append(history:M.blank_history,route_a:true,informed:true,payoff_tenths:10,num_a:Object.new)}
  end
  def test_informed_exact
    assert_equal Rational(1,2),M.informed_probability([],q:1)
    assert_equal Rational(1,2),M.informed_probability([10,-10],q:1)
    assert_equal Rational(1,2),M.informed_probability([10,-10],q:2)
    assert_equal Rational(2,3),M.informed_probability([10,10,-10],q:1)
  end
  def test_uninformed_separate_reward_pool
    assert_equal Rational(1,2),M.uninformed_probability([],[-10],q:3)
    assert_equal 1,M.uninformed_probability([20],[10],q:5)
    assert_equal 0,M.uninformed_probability([0],[10],q:5)
    assert_equal Rational(1,2),M.uninformed_probability([10],[10],q:9)
    assert_equal Rational(1,2),M.uninformed_probability([10,20],[15],q:1)
  end
  def test_informed_counterfactual_uses_opponents_only
    h=M.blank_history
    M.append(history:h,route_a:true,informed:true,payoff_tenths:97,num_a:5)
    assert_equal [-10],h[:paired_differences]
    M.append(history:h,route_a:false,informed:true,payoff_tenths:50,num_a:3)
    assert_equal [-10,20],h[:paired_differences]
  end
  def test_mass_and_error_checks
    assert_equal({0=>1,1=>2,2=>1},M.distribution([0,1],2))
    assert_raises(ArgumentError){M.distribution([],1)}
    assert_raises(ArgumentError){M.distribution([0],10)}
    assert_raises(ArgumentError){M.prior_mixture(history:M.blank_history,informed:true,max_q:0)}
  end
end
