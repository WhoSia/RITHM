# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'exact_frontier'
class TestExactFrontier < Minitest::Test
 M=RithmExactFrontier
 def test_exact_intervals_and_boundary
  a=M.intervals
  assert_equal 10,a.size
  assert_equal 9,a.count{|x|x.fetch('q_upper')==0 || x.fetch('q_upper')==Rational(1,8)}
  assert_equal 1,a.count{|x|x.fetch('upper_unbounded')}
  [0,Rational(1,16),Rational(1,8),Rational(3,16),1].each do |q|
   from_intervals=a.select{|x|x.fetch('q_lower')<=q&&(x.fetch('q_upper').nil?||q<=x.fetch('q_upper'))}
   direct=RithmThreeAgentInspection.audit(q:q).fetch('pure_equilibria')
   assert_equal direct.size,from_intervals.size
  end
 end
 def test_restricted_mixed_support
  assert_equal Rational(1,8),M.restricted_mixed(q:0).fetch('inspection_probability')
  assert_equal Rational(1,16),M.restricted_mixed(q:Rational(1,16)).fetch('inspection_probability')
  assert_equal 0,M.restricted_mixed(q:Rational(1,8)).fetch('inspection_probability')
  refute M.restricted_mixed(q:Rational(1,16)).fetch('full_game_mixed_nash_verified')
 end
end
