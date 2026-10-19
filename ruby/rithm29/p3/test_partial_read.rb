# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'partial_read'
class TestPartialRead < Minitest::Test
 def test_paid_inert_partial_read_dominated
  a=Rithm29PartialRead.check(read_fee:Rational(1,4),full_fee:1,switch:Rational(1,2))
  assert_equal 18,a[:rows].length
  assert a[:dominated]
 end
 def test_zero_fee_only_weak_dominance
  refute Rithm29PartialRead.check(read_fee:0,full_fee:1,switch:0)[:dominated]
 end
end
