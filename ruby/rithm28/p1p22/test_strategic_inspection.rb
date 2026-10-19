# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'strategic_inspection'
class TestStrategicInspection < Minitest::Test
 M=RithmStrategicInspection
 def test_full_pure_equilibrium_court_corrects_level_zero_paradox
  r=M.equilibria
  assert_equal 36,r.fetch('all_pure_contingent_profiles_checked')
  assert_equal 2,r.fetch('pure_equilibria').size
  expected=[[false,0,0],[true,0,1]]
  assert_equal [expected,expected.reverse],r.fetch('pure_equilibria').map{|e|e.fetch('plans')}
  assert r.fetch('pure_equilibria').all?{|e|e.fetch('social_cost')==Rational(95,16)}
  assert_operator Rational(95,16),:<,6
  assert_equal false,r.fetch('mixed_equilibria_examined')
 end
 def test_independent_alternative_is_not_profitable
  r=M.equilibria
  r.fetch('pure_equilibria').each do |e|
   ps=e.fetch('plans')
   2.times do |i|
    M::PLANS.each do |alt|
     changed=ps.dup; changed[i]=alt
     assert_operator M.expected(changed,k:Rational(3,4),q:Rational(1,16),p:Rational(1,2)).fetch('individual')[i],
       :>=,e.fetch('individual_cost')[i]
    end
   end
  end
 end
 def test_invalid_parameters
  assert_raises(ArgumentError){M.equilibria(k:-1)}
  assert_raises(ArgumentError){M.equilibria(q:-1)}
  assert_raises(ArgumentError){M.equilibria(p:2)}
 end
end
