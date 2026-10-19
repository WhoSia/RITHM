# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'dynamic_court'
class TestRithm29DynamicCourt < Minitest::Test
 M=Rithm29DynamicCourt
 def test_subgame_pure_nash_in_all_public_memory_states
  a=M.run(horizon:3)
  assert_equal 12,a[:policies].size
  assert a[:policies].values.all?{|v|v[:equilibrium_count]>0}
  a[:policies].each do |(t,prev),row|
   e=row[:selected]
   assert row[:all_equilibria].include?(e)
   assert_equal 2,e[:costs].size
  end
 end
 def test_zero_switch_fee_one_round_agrees_with_original
  a=M.run(horizon:1,switch_fee:0)
  assert_equal 5,a[:expected_social]
 end
 def test_nonempty_exact_finite_horizon
  a=M.run(horizon:2)
  assert a[:expected_social].is_a?(Rational)
  refute a[:unique_equilibrium_certified]
 end
end
