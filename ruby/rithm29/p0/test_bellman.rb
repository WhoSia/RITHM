# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'bellman'
class TestBellman < Minitest::Test
 M=Rithm29Bellman
 def test_one_round_threshold
   assert_equal Rational(5,2),M.solve(horizon:1,fee:1,k:Rational(1,2))[:value]
   assert_equal :stop,M.solve(horizon:1,fee:1,k:Rational(1,2))[:policy][[1,0]][:instruction]
   assert_equal :inspect,M.solve(horizon:1,fee:0,k:Rational(1,2))[:policy][[1,0]][:instruction]
 end
 def test_finite_dynamic_program
   v=M.solve(horizon:3)
   assert_equal 3,v[:horizon]
   assert v[:value].is_a?(Rational)
   assert_equal 6,v[:policy].size
   refute v[:strategic_game_equilibrium]
 end
 def test_more_information_is_not_forced
   assert_operator M.solve(horizon:3,fee:0)[:value],:<=,M.solve(horizon:3,fee:2)[:value]
 end
end
