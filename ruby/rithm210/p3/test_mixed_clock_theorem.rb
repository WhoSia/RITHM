require 'minitest/autorun'
require_relative 'mixed_clock_theorem'
class TestMixedClockTheorem < Minitest::Test
  M=Rithm210MixedClockTheorem
  def test_closed_form_matches_independent_rational_gaussian_elimination
    [0,Rational(1,10),Rational(1,2),Rational(3,4),Rational(9,10),
      Rational(99,100),Rational(999,1000)].each do |s|
      assert_equal M.closed_form_t3(sync:s),
        Rithm210MixedClockChain.expected_hitting_times(sync:s)[3]
    end
  end
  def test_quadratic_synchronization_singularity
    [Rational(9,10),Rational(99,100),Rational(999,1000)].each do |s|
      assert_operator M.exact_limit_gap(sync:s),:>,0
    end
    assert_operator M.exact_limit_gap(sync:Rational(99,100)).abs,:<,
      M.exact_limit_gap(sync:Rational(9,10)).abs
    assert_raises(ArgumentError){M.closed_form_t3(sync:1)}
  end
end
