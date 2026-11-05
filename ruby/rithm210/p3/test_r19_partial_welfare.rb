require 'minitest/autorun'
require_relative 'r19_partial_welfare'
class TestRithm210R19PartialWelfare < Minitest::Test
  M=Rithm210R19PartialWelfare
  ZERO=Array.new(6,0.to_r)
  def test_exact_cost_and_labeled_support
    assert_equal 24,M.cost(15)
    assert_equal 27,M.cost(7)
    assert_equal 36,M.cost(3)
    assert_equal 20,M.envelope(observed_n:3,p_a:ZERO,p_b:ZERO,horizon:2)[:compositions]
  end
  def test_baseline_is_observationally_equal
    x=M.envelope(observed_n:3,p_a:ZERO,p_b:ZERO,horizon:40)
    assert_equal 1080,x[:minimum]
    assert_equal 1080,x[:maximum]
    assert_equal 0,x[:width]
  end
  def test_sharp_effect_interval_sign_reversal
    r=M.counterexample
    assert_equal 1020,r[:intervention][:minimum]
    assert_equal 1260,r[:intervention][:maximum]
    assert_equal 240,r[:intervention][:width]
    assert_equal [-60,180],r[:treatment_effect_range]
    refute_equal r[:intervention][:minimizer]&1,r[:intervention][:maximizer]&1
  end
  def test_last_round_action_cannot_change_current_cost
    pa,pb=M.toggle_actor_zero
    assert_equal 27,M.envelope(observed_n:3,p_a:pa,p_b:pb,horizon:1)[:minimum]
    assert_equal 27,M.envelope(observed_n:3,p_a:pa,p_b:pb,horizon:1)[:maximum]
  end
  def test_rational_mass_conservation
    pa=Array.new(6,1.to_r/2);pb=ZERO
    k=M.kernel(p_a:pa,p_b:pb)
    assert k.all?{|row|row.values.sum==1}
    assert k.any?{|row|row.values.any?{|pr|pr.denominator>1}}
    assert M.values(p_a:pa,p_b:pb,horizon:3).all?{|v|v.is_a?(Rational)}
  end
  def test_reject_invalid_probabilities
    assert_raises(ArgumentError){M.values(p_a:[0.5]*6,p_b:ZERO,horizon:2)}
    assert_raises(ArgumentError){M.values(p_a:ZERO,p_b:ZERO,horizon:0)}
    assert_raises(ArgumentError){M.envelope(observed_n:7,p_a:ZERO,p_b:ZERO,horizon:1)}
  end
end
