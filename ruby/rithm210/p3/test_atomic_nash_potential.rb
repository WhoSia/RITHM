require 'minitest/autorun'
require_relative 'atomic_nash_potential'
class TestRithm210AtomicNash < Minitest::Test
  M=Rithm210AtomicNash
  def test_all_unilateral_moves_have_exact_potential_difference
    (0..5).each do |n|
      assert_equal M.b_to_a_cost_change(n),M.potential(n+1)-M.potential(n)
    end
    (1..6).each do |n|
      assert_equal M.a_to_b_cost_change(n),M.potential(n-1)-M.potential(n)
    end
  end
  def test_unique_nash_occupancy_and_social_optimum
    a=M.equilibrium_summary
    assert_equal [4],a[:nash_occupancies]
    assert_equal [4],a[:socially_optimal_occupancies]
    assert_equal 15,a[:number_of_pure_nash_action_profiles]
    assert_equal 24,a[:group_optimum_cost]
    assert_equal 16,a[:potential_at_optimum]
    assert_equal 2,a[:a_to_b_loss_at_n4]
    assert_equal 1,a[:b_to_a_loss_at_n4]
  end
  def test_costs_for_every_integer_occupancy
    assert_equal [72,51,36,27,24,27,36],(0..6).map{|n|M.group_cost(n)}
  end
end
