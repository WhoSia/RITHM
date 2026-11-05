require 'minitest/autorun'
require_relative 'labeled_smooth_welfare_rollout'
class TestRithm210LabeledSmoothWelfareRollout < Minitest::Test
  M=Rithm210LabeledSmoothWelfareRollout
  S=Rithm210SmoothClockWelfareRollout
  def test_labeled_equals_seven_state_when_all_agents_exchangeable
    [0.05,0.3].each do |k|
      a=M.evaluate(clock: :simultaneous,signal: :frozen,strength:k,initial_mask:15)
      b=S.evaluate(clock: :simultaneous,signal: :frozen,strength:k,initial:4)
      assert_in_delta b[:cumulative_excess],a[:cumulative_excess],1e-9
      assert_in_delta 1.0,a[:terminal_microstate].sum,1e-10
    end
  end
  def test_same_occupancy_different_actor_composition_affects_welfare
    params={clock: :simultaneous,signal: :frozen,strength:0.7,biases:[2.0,0,0,0,0,0]}
    a=M.evaluate(initial_mask:15,**params)
    b=M.evaluate(initial_mask:30,**params)
    assert_operator (a[:cumulative_excess]-b[:cumulative_excess]).abs,:>,0.2
  end
  def test_heterogeneous_transition_rows_have_unit_mass
    k=M.kernel(clock: :sequential,signal: :refreshed,strength:0.7,biases:[2,0,0,0,0,0])
    assert_equal 64,k.size
    k.each{|row|assert_in_delta 1,row.sum,1e-10}
  end
end
