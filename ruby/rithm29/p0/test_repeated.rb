# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'repeated'
class TestRithm29Repeated < Minitest::Test
 M=Rithm29Repeated
 def test_exhaustive_three_period_contract
  r=M.comparison
  assert_equal 4,r.size
  assert r.all?{|x|x[:trajectories]==64}
  assert_equal 18,r[0][:expected_total]
  assert_equal Rational(63,4),r[1][:expected_total]
  assert_equal Rational(63,4),r[2][:expected_total]
  assert_equal Rational(39,2),r[3][:expected_total]
 end
 def test_zero_switch_fee_recovers_one_round_cost
  r=M.comparison(horizon:3,switch_fee:0)
  assert_equal [18,15,15,18],r.map{|x|x[:expected_total]}
 end
 def test_not_a_repeated_equilibrium_proof
  refute M.comparison.first[:long_run_equilibrium_verified]
 end
end
