require 'minitest/autorun'
require_relative 'adaptation_cycle'
class TestRithm210AdaptationCycle < Minitest::Test
  M=Rithm210AdaptationCycle
  def test_exact_cycle_and_threshold
    c=M.cycle(rho:Rational(1,8))
    assert_equal Rational(7,15),c[:low]
    assert_equal Rational(8,15),c[:high]
    assert_equal Rational(1,15),c[:critical_kappa]
    assert_equal Rational(1,450),c[:excess_cost_each_period]
    assert_equal Rational(49,64),c[:two_step_contraction]
  end
  def test_strict_switch_and_equality_stops
    assert M.verify_step(rho:Rational(1,8),kappa:Rational(1,20))
    assert M.verify_step(rho:Rational(1,8),kappa:0)
    refute M.strict_two_cycle?(rho:Rational(1,8),kappa:Rational(1,15))
    refute M.strict_two_cycle?(rho:Rational(1,8),kappa:Rational(1,5))
  end
  def test_pulse_stickiness_and_cost
    p=M.one_pulse_lockin(kappa:Rational(1,5),rho:Rational(1,8),signal:Rational(2,5))
    assert_equal Rational(7,16),p[:post_signal_fraction]
    assert_equal Rational(1,128),p[:persistent_excess]
    assert_raises(ArgumentError){M.one_pulse_lockin(
      kappa:Rational(1,5),rho:Rational(1,8),signal:Rational(1,5))}
  end
  def test_discounted_welfare_formula
    assert_equal Rational(1,8),M.discounted_tail(
      excess:Rational(1,100),discount:Rational(23,25))
    assert_equal Rational(1,100),M.discounted_tail(
      excess:Rational(1,100),discount:Rational(23,25),periods:1)
    assert_equal Rational(12,625),M.discounted_tail(
      excess:Rational(1,100),discount:Rational(23,25),periods:2)
  end
  def test_vanishing_friction_discounted_effect
    [Rational(1,5),Rational(1,20),Rational(1,100)].each do |k|
      v=M.vanishing_friction_long_horizon(kappa:k)
      assert_equal k*k/8,v[:flow_excess]
      assert_equal Rational(1,8),v[:infinite_discounted_excess]
    end
  end
  def test_invalid_parameters
    assert_raises(ArgumentError){M.cycle(rho:0)}
    assert_raises(ArgumentError){M.cycle(rho:1)}
    assert_raises(ArgumentError){M.strict_two_cycle?(rho:Rational(1,5),kappa:-1)}
    assert_raises(ArgumentError){M.discounted_tail(excess:1,discount:1)}
  end
end
