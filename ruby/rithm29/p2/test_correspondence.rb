# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'correspondence'
class TestCorrespondence < Minitest::Test
 def test_all_three_program_correspondences
  a=Rithm29Correspondence.enumerate(horizon:3)
  assert a[:complete]
  assert_equal [16,408,13568],a[:branch_counts]
  assert_equal Rational(25,2),a[:minimum]
  assert_equal 15,a[:maximum]
  assert_equal [Rational(25,2),Rational(27,2),14,Rational(29,2),15],a[:welfare_values]
 end
 def test_admits_keep_previous_without_computation
  zero=Rithm29Correspondence::STATES.to_h{|s|[s,[0,0]]}
  eq=Rithm29Correspondence.state_equilibria(zero,[1,1],fee:1,switch:Rational(1,2),wrong:2)
  assert_equal [[:stop0,:stop1],[:stop1,:stop0]],eq.map(&:first)
 end
 def test_limited_horizon_reports_incomplete
  a=Rithm29Correspondence.enumerate(horizon:3,limit:20)
  refute a[:complete]
 end
end
