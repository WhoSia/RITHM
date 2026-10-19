# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'three_agent'
class TestThreeAgent < Minitest::Test
 M=RithmThreeAgentInspection
 def test_all_three_are_strategic
  r=M.audit
  assert_equal 216,r.fetch('profiles')
  assert_equal 6,r.fetch('depth')
  assert_equal 'NOT CHECKED',r.fetch('mixed_equilibrium')
  r.fetch('pure_equilibria').each do |eq|
   M::PLANS.each do |alt|
    3.times do |i|
     newplans=eq.fetch('plans').dup;newplans[i]=alt
     assert_operator M.expected(newplans,k:Rational(3,4),q:Rational(1,16),p:Rational(1,2))[0][i],:>=,eq.fetch('individual')[i]
    end
   end
  end
 end
 def test_information_fees_and_switch_costs_differ
  ps=[[false,0,0],[false,0,0],[false,1,1]]
  assert_equal 0,M.result(ps,0,1,1)[0][0]-M.result(ps,0,0,1)[0][0]
  check=[[true,0,0],[false,0,0],[false,1,1]]
  assert_equal 1,M.result(check,0,0,1)[0][0]-M.result(check,0,0,0)[0][0]
 end
 def test_depth_screen_is_not_equilibrium_claim
  a=M.audit(depth:2);b=M.audit(depth:6)
  assert_operator a.fetch('depth_limited_stable'),:>=,b.fetch('pure_equilibria').size
 end
end
