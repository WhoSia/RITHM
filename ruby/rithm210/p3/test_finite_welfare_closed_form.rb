require 'minitest/autorun'
require_relative 'finite_welfare_closed_form'
class TestRithm210FiniteWelfareClosedForm < Minitest::Test
  M=Rithm210FiniteWelfareClosedForm
  D=Rithm210FiniteHorizonIndependentWelfare
  def test_closed_form_matches_full_seven_state_chain_for_two_rates
    [Rational(1,10),Rational(1,4)].each do |a|
      r=D.run(a:a,b:2*a,horizon:40)
      (0...40).each do |t|
        assert_equal M.excess_at(a:a,period:t),r[:path][t][:excess]
      end
      assert_equal M.cumulative(a:a,horizon:40),r[:cumulative_discounted_excess]
    end
  end
  def test_same_stationary_but_different_transient_welfare
    assert_equal Rational(51,25),M.excess_at(a:Rational(1,10),period:1)
    assert_equal Rational(15,4),M.excess_at(a:Rational(1,4),period:1)
    assert_equal 0,M.excess_at(a:Rational(1,10),period:0)
    assert_operator M.cumulative(a:Rational(1,4),horizon:40),:>,M.cumulative(a:Rational(1,10),horizon:40)
  end
  def test_input_guards
    assert_raises(ArgumentError){M.cumulative(a:0,horizon:40)}
    assert_raises(ArgumentError){M.cumulative(a:Rational(3,4),horizon:40)}
    assert_raises(ArgumentError){M.cumulative(a:Rational(1,10),horizon:0)}
    assert_raises(ArgumentError){M.excess_at(a:Rational(1,10),period:-1)}
  end
end
