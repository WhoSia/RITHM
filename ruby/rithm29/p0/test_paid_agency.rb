# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'paid_agency'
class TestPaidAgency < Minitest::Test
 M=Rithm29PaidAgency
 def test_exact_p0_equilibrium_court
  a=M.audit
  assert_equal 4,a.fetch(:rows).size
  assert_equal [[:stop,:compute],[:compute,:stop]],a.fetch(:pure_equilibria).map{|x|x[:policies]}
  assert_equal [6,5,5,6],a.fetch(:rows).map{|x|x[:social]}
  assert_equal [Rational(5,2),Rational(5,2)],a.fetch(:rows)[1][:individual]
  assert_equal [3,3],a.fetch(:rows)[0][:individual]
  assert_equal Rational(1,2),a.fetch(:symmetric_mixed).fetch(:probability_compute)
  assert_equal Rational(11,2),a.fetch(:symmetric_mixed).fetch(:social)
 end
 def test_paid_instruction_trace
  a=M.outcome([:compute,:stop],[0,1],read_fee:Rational(1,4),xor_fee:Rational(1,2),mismatch_loss:2)
  assert_equal [:read_x,:read_y,:xor,:act],a[:traces][0][:instructions]
  assert_equal 1,a[:traces][0][:computation_cost]
  assert_equal [1,0],a[:routes]
 end
 def test_boundary_model_not_universal
  a=M.audit(read_fee:2,xor_fee:3)
  assert_nil a.fetch(:symmetric_mixed)
  assert_equal [[:stop,:stop]],a.fetch(:pure_equilibria).map{|x|x[:policies]}
 end
end
