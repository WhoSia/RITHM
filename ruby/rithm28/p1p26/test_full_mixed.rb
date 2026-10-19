# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'full_mixed'
class TestFullMixed < Minitest::Test
 M=RithmFullMixedCourt
 def test_exact_probability_and_full_deviations
   a=M.certificate(q:Rational(1,16))
   assert_equal Rational(1,16),a.fetch('x')
   assert_equal Rational(79,32),a.fetch('expected_individual_losses')[0][0]
   assert_equal Rational(79,32),a.fetch('expected_individual_losses')[0][3]
   assert a.fetch('full_game_deviations_verified')
 end
 def test_entire_rational_support_grid
   (0..8).each do |j|
     a=M.certificate(q:Rational(j,64))
     assert_equal Rational(8-j,64),a.fetch('x')
   end
 end
 def test_outside_support_rejected
   assert_raises(ArgumentError){M.certificate(q:Rational(9,64))}
 end
end
