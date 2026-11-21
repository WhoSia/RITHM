# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_identification'
class T13IdentificationTest < Minitest::Test
  I=RithmT13::Identification
  def test_observational_equivalence
    x=I.exact_equivalent_cases
    assert_equal Rational(1,10),x[:a]
    assert_equal x[:a],x[:b]
  end
  def test_no_attention
    assert_equal 0,I.positive_gain_flip(opportunity:1,attention:0)
  end
  def test_probability_gate
    assert_raises(ArgumentError){I.positive_gain_flip(opportunity:Rational(5,4),attention:1)}
  end
end
