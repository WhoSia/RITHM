require 'minitest/autorun'
require_relative 'update_clock_welfare_rollout'
class TestRithm210UpdateClockWelfareRollout < Minitest::Test
  M=Rithm210UpdateClockWelfareRollout
  def test_kernels_stochastic
    [:simultaneous,:sequential].each do |clock|
      [:frozen,:refreshed].each do |signal|
        k=M.kernel(clock:clock,signal:signal)
        assert_equal 7,k.size
        k.each do |row|
          assert_equal 7,row.size
          assert_in_delta 1.0,row.sum,1e-12
          assert row.all?{|v|v>=0 && v<=1}
        end
      end
    end
  end
  def test_first_observed_state_and_next_expected_cost
    a=M.evaluate(clock: :sequential,signal: :refreshed,horizon:2)
    assert_equal 0.0,a[:path].first[:expected_excess]
    assert_in_delta 0.6297984,a[:path][1][:expected_excess],1e-12
    assert_equal 6,a[:opportunities_per_round]
  end
  def test_frozen_schedule_invariant_and_40round_difference
    x=M.factorial
    q=x[:protocols]
    a=q.fetch([:simultaneous,:frozen])[:cumulative_excess]
    assert_in_delta a,q.fetch([:simultaneous,:refreshed])[:cumulative_excess],1e-9
    assert_in_delta a,q.fetch([:sequential,:frozen])[:cumulative_excess],1e-9
    b=q.fetch([:sequential,:refreshed])[:cumulative_excess]
    assert_in_delta 705.2720417083509,a,1e-7
    assert_in_delta 24.288573009427733,b,1e-7
    assert_in_delta b-a,x[:interaction],1e-7
  end
  def test_invalid_or_no_tremble
    assert_raises(ArgumentError){M.evaluate(clock: :simultaneous,signal: :frozen,horizon:0)}
    assert_raises(ArgumentError){M.evaluate(clock: :simultaneous,signal: :frozen,initial:7)}
    x=M.evaluate(clock: :sequential,signal: :refreshed,tremble:0.to_r)
    assert_in_delta 0.0,x[:cumulative_excess],1e-12
  end
end
