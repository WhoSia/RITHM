require 'minitest/autorun'
require_relative 'adjustment_clocks'
class TestRithm210AdjustmentClocks < Minitest::Test
  M=Rithm210AdjustmentClocks
  def test_synchronous_overshoot_and_social_cost
    a=M.audit
    assert_equal({0=>6,1=>6,2=>6,3=>6,4=>4,5=>0,6=>0},a[:synchronous])
    assert_equal 54,a[:two_cycle_mean_group_congestion]
    assert_equal 30,a[:cycle_mean_excess]
    (0..6).each{|n|assert_equal(n==4 ? [4] : [0,6],M.synchronous_attractor(n))}
  end
  def test_asynchronous_each_profitable_move_reduces_congestion_cost
    (0..6).each do |n|
      [:a,:b].each do |who|
        next if who==:a && n==0 || who==:b && n==6
        nxt=M.asynchronous(n,who:who)
        assert_operator Rithm210AtomicNash.group_cost(nxt),:<=,
          Rithm210AtomicNash.group_cost(n)
        assert_operator (nxt-4).abs,:<=,(n-4).abs
      end
    end
  end
  def test_exact_one_actor_random_schedule_expected_hitting_time
    assert_in_delta 5.7,M.expected_async_hitting_time(0),1e-12
    assert_in_delta 2.2,M.expected_async_hitting_time(6),1e-12
    assert_in_delta 1.2,M.expected_async_hitting_time(5),1e-12
    assert_equal 0,M.expected_async_hitting_time(4)
  end
  def test_snapshot_game_nash_is_fixed_for_both_schedules
    assert_equal 4,M.synchronous(4)
    assert_equal 4,M.asynchronous(4,who: :a)
    assert_equal 4,M.asynchronous(4,who: :b)
  end
end
