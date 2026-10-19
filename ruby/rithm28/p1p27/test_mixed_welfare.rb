# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'mixed_welfare'
class TestMixedWelfare < Minitest::Test
 def test_exact_social_cost_identity_in_full_mixed_family
   (0..16).each do |i|
     r=RithmMixedWelfare.decomposition(q:Rational(i,128))
     assert_equal 6,r.fetch('mixed_welfare')
   end
 end
 def test_nonzero_information_acquisition_without_welfare_gain
   r=RithmMixedWelfare.decomposition(q:Rational(1,16))
   assert_equal Rational(1,16),r.fetch('x')
   assert_equal Rational(95,16),r.fetch('one_inspector')
   assert_equal Rational(63,8),r.fetch('two_inspectors')
 end
end
