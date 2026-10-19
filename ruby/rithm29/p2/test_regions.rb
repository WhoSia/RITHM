# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'regions'
class TestOnePeriodRegions < Minitest::Test
 def test_affine_inequalities_against_independent_direct_payoff_court
  court=Rithm29Correspondence;region=Rithm29OnePeriodRegions
  zero=court::STATES.to_h{|s|[s,[0,0]]}
  court::STATES.each do |prev|
   (0..4).each do |i|
    (0..4).each do |j|
     fee=Rational(i,4);k=Rational(j,4)
     direct=court.state_equilibria(zero,prev,fee:fee,switch:k,wrong:2).map(&:first)
     assert_equal direct,region.equilibria(previous:prev,fee:fee,switch:k,wrong:2)
    end
   end
  end
 end
 def test_one_round_three_action_basepoint
  region=Rithm29OnePeriodRegions
  assert_equal [[:stop0,:stop1],[:stop1,:stop0]],region.equilibria(previous:[0,0],fee:1,switch:Rational(1,2))
 end
end
