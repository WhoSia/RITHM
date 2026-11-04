require 'minitest/autorun'
require_relative 'friction_welfare'
class TestRithm210FrictionWelfare < Minitest::Test
  M=Rithm210FrictionWelfare
  def test_band_and_bound
    k=Rational(1,5)
    assert_equal [Rational(2,5),Rational(3,5)],M.interior_stationary_band(k:k)
    assert M.stationary?(x:Rational(2,5),k:k)
    assert M.stationary?(x:Rational(3,5),k:k)
    refute M.stationary?(x:Rational(7,20),k:k)
    assert_equal Rational(1,50),M.inertia_bound(k:k)
    assert_equal Rational(1,50),M.excess_at_zero_bias(x:Rational(3,5))
    assert_equal Rational(1,50),M.excess_at_zero_bias(x:Rational(2,5))
  end
  def test_no_friction_interior_unique
    assert M.stationary?(x:Rational(1,2),k:0)
    refute M.stationary?(x:Rational(49,100),k:0)
    refute M.stationary?(x:Rational(51,100),k:0)
  end
  def test_pulse_generates_persistent_cost_even_after_exogenous_bias_clears
    r=M.pulse_example
    assert_equal Rational(7,16),r[:after_pulse]
    assert_equal Rational(7,16),r[:after_return]
    assert_equal Rational(1,2),r[:no_pulse]
    assert r[:stationary_after_return]
    assert_equal Rational(65,128),r[:pulse_path_cost]
    assert_equal Rational(1,2),r[:no_pulse_path_cost]
    assert_equal Rational(1,128),r[:persistent_welfare_excess]
  end
  def test_no_switch_at_equality
    assert_equal Rational(3,5),M.step(x:Rational(3,5),k:Rational(1,5),rho:1)
    assert_equal Rational(2,5),M.step(x:Rational(2,5),k:Rational(1,5),rho:1)
  end
  def test_reject_bad_inputs
    assert_raises(ArgumentError){M.step(x:0,k:Rational(3,2),rho:Rational(1,2))}
    assert_raises(ArgumentError){M.step(x:0,k:0,rho:Rational(3,2))}
    assert_raises(ArgumentError){M.stationary?(x:Rational(-1,10),k:0)}
  end
end
