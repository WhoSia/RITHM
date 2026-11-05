require 'minitest/autorun'
require_relative 'smooth_clock_welfare_rollout'
class TestRithm210SmoothClockWelfareRollout < Minitest::Test
  M=Rithm210SmoothClockWelfareRollout
  def test_frozen_clock_is_schedule_invariant
    a=M.kernel(clock: :simultaneous,signal: :frozen,strength:0.3)
    b=M.kernel(clock: :sequential,signal: :frozen,strength:0.3)
    (0..6).each do |n|
      assert_in_delta 1.0,a[n].sum,1e-10
      a[n].zip(b[n]).each{|u,v|assert_in_delta u,v,1e-10}
    end
  end
  def test_short_term_worsening_and_long_term_improvement
    short=Rithm210SmoothSignalClock.factorial(mask:0,strength:0.05,tremble:0.1)
    long=M.contrast(initial:0,strength:0.05)
    assert_operator short[:interaction],:>,0
    assert_in_delta(-25.64999,long[:interaction],1e-4)
    assert_operator long[:interaction],:<,0
  end
  def test_zero_strength_and_initial_cost
    assert_in_delta 48,M.evaluate(clock: :simultaneous,signal: :frozen,strength:0.2,initial:0,horizon:1)[:cumulative_excess],1e-10
    assert_in_delta 0,M.contrast(initial:4,strength:0)[:interaction],1e-10
  end
  def test_heterogeneous_occupancy_projection_blocked
    assert_raises(ArgumentError){M.kernel(clock: :simultaneous,signal: :frozen,strength:0.2,biases:[1,0,0,0,0,0])}
  end
end
