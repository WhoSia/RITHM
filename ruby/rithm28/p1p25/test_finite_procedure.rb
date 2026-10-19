# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'finite_procedure'
class TestFiniteProcedure < Minitest::Test
 M=RithmFiniteProcedure
 def test_nonmyopic_computation_complementarity
  r=M.solve(read_fee:Rational(1,4),xor_fee:Rational(1,2))
  assert_equal 2,r.fetch('stop_expected_cost')
  assert_equal Rational(9,4),r.fetch('one_probe_then_stop_cost')
  assert_equal 1,r.fetch('two_reads_and_compute_cost')
  assert_equal 'READ_X;READ_Y;XOR;ACT',r.fetch('optimal_policy')
  assert_operator r.fetch('one_step_improvement'),:<,0
 end
 def test_expensive_compute_prevents_reading
  r=M.solve(read_fee:Rational(1,4),xor_fee:2)
  assert_equal 'STOP;ACT_CONSTANT',r.fetch('optimal_policy')
 end
 def test_fee_zero_tie_stop
  r=M.solve(read_fee:0,xor_fee:2)
  assert_equal 'STOP;ACT_CONSTANT',r.fetch('optimal_policy')
 end
end
