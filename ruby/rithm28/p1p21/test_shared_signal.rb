# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'shared_signal'
class TestSharedSignal < Minitest::Test
 M=RithmSharedSignal
 def test_costly_attention_private_value_collective_harm
  r=M.evaluate(k:Rational(3,4),q:Rational(1,16))
  assert r.fetch('inspect')
  assert_equal Rational(1,8),r.fetch('information_value')
  assert_equal 6,r.fetch('uninspected_expected_cost')
  assert_equal Rational(63,8),r.fetch('inspected_expected_cost')
  assert_equal Rational(15,8),r.fetch('cost_delta')
  assert_equal false,r.fetch('strategic_equilibrium_verified')
 end
 def test_attention_fee_threshold
  assert M.evaluate(k:Rational(3,4),q:Rational(1,16)).fetch('inspect')
  refute M.evaluate(k:Rational(3,4),q:Rational(1,8)).fetch('inspect')
 end
 def test_cost_externality_and_avoidance
  r=M.evaluate(k:Rational(3,4),q:0)
  assert_equal [1,1,1],r.fetch('outcomes')[1].fetch('routes')
  refute M.evaluate(k:Rational(3,4),q:1).fetch('inspect')
 end
 def test_other_regimes_not_proclaimed
  assert_raises(ArgumentError){M.evaluate(k:0,q:0)}
 end
end
