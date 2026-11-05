require 'minitest/autorun'
require_relative 'general_adjustment_clocks'
class TestRithm210GeneralAdjustmentClocks < Minitest::Test
  M=Rithm210GeneralAdjustmentClocks
  def test_exact_potential_all_actions_N3_to_15
    (3..15).each do |total|
      (0...total).each do |n|
        assert_equal M.b_to_a_change(n,total:total),
          M.potential(n+1,total:total)-M.potential(n,total:total)
      end
      (1..total).each do |n|
        assert_equal M.a_to_b_change(n,total:total),
          M.potential(n-1,total:total)-M.potential(n,total:total)
      end
    end
  end
  def test_all_multiple_of_three_have_same_9_over_4_cycle_ratio
    [3,6,9,12,15,30].each do |n|
      r=M.theorem_divisible_by_three(total:n)
      assert_equal Rational(9,4),r[:ratio]
      assert_equal Rational(5*n*n,6),r[:dynamic_excess]
      assert_equal [2*n/3],M.nash_states(total:n)
      assert_equal [2*n/3],M.optimal_states(total:n)
    end
  end
  def test_nonmultiple_of_three_need_not_have_unique_nash
    assert_equal [3,4],M.nash_states(total:5)
    assert_equal [3],M.optimal_states(total:5)
    assert_equal [3],M.nash_states(total:4)
  end
  def test_reject_bad_domain
    assert_raises(ArgumentError){M.theorem_divisible_by_three(total:5)}
    assert_raises(ArgumentError){M.cost(2,total:2)}
  end
end
