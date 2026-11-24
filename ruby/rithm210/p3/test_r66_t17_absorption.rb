# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t17_absorption'
class T17AbsorptionTest < Minitest::Test
  A=RithmT17::Absorption;O=RithmT17::Oracle
  def test_interval_and_strict_interior
    assert_equal [Rational(1,5),Rational(1,2)],A.interval
    assert_equal [Rational(-1,5),Rational(-1)],A.gains_at_five(Rational(2,5))
    assert_equal [Rational(2,25),Rational(4,5)],A.interval(Rational(3,5))
  end
  def test_theory_matches_exact_transition
    [0,Rational(1,5),Rational(3,5),1].each do |c|
      (0..10).each do |i|
        r=Rational(i,10)
        [:common,:independent,:fixed_three].each do |clock|
          row=O.row(5,clock:clock,rho:r,disclosure:1,response:1,threshold:c)
          assert_equal A.trapped?(r,c),row[5]==1
        end
      end
    end
  end
  def test_invalid_threshold
    assert_raises(ArgumentError){A.interval(-1)}
  end
end
