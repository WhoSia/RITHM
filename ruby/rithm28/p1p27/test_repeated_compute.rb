# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'repeated_compute'
class TestRepeatedCompute < Minitest::Test
 def test_cost_savings_scale_under_independent_reset
  r=RithmRepeatedCompute.compare(rounds:4,read_fee:Rational(1,4),xor_fee:Rational(1,2))
  assert_equal 4,r.fetch('compute_all_expected_cost')
  assert_equal 8,r.fetch('never_compute_expected_cost')
  assert r.fetch('compute_all_better')
 end
 def test_policy_refresh_cost_can_reverse_decision
  r=RithmRepeatedCompute.compare(rounds:4,read_fee:Rational(1,4),xor_fee:Rational(1,2),reset_cost:2)
  assert_equal 10,r.fetch('compute_all_expected_cost')
  refute r.fetch('compute_all_better')
 end
 def test_contract_not_a_game_equilibrium
  r=RithmRepeatedCompute.compare(rounds:2,read_fee:0,xor_fee:0)
  refute r.fetch('mixed_strategy_equilibrium')
 end
end
