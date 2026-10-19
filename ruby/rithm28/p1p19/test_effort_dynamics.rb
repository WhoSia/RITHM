# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'effort_dynamics'
class TestEffortDynamics < Minitest::Test
 M=RithmEffortDynamics
 def test_parallel_synchrony_creates_two_cycle
  assert_equal [[0,0,0],[1,1,1],[0,0,0],[1,1,1]],M.trajectory([0,0,0],horizon:3)
  assert_equal [0,0,1],M.advance([0,0,1])
  r=M.verdict(horizon:4)
  assert_equal [20,0],r.fetch('cumulative_cost_errors')
  assert r.fetch('ranking_reversal')
 end
 def test_asynchronous_dissipates_cost_difference_after_one_step
  assert_equal [1,0,0],M.advance([0,0,0],schedule: :sequential)
  r=M.verdict(horizon:4,schedule: :sequential)
  assert_equal [4,0],r.fetch('cumulative_cost_errors')
 end
 def test_large_switching_friction_fixes_all_zero_state
  assert_equal [0,0,0],M.advance([0,0,0],friction:2)
  assert_equal [0,0,0],M.advance([0,0,0],friction:3)
 end
 def test_friction_one_insufficient_to_stop_three_agent_cycling
  assert_equal [1,1,1],M.advance([0,0,0],friction:1)
 end
 def test_bad_contract_rejected
  assert_raises(ArgumentError){M.advance([0,0,0],friction:-1)}
  assert_raises(ArgumentError){M.trajectory([0,0,0],horizon:30)}
 end
end
