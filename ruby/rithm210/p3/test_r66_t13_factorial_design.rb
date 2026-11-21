# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_factorial_design'
class T13FactorialDesignTest < Minitest::Test
  D=RithmT13::FactorialDesign
  def test_multiple_mechanisms_same_switch_probability
    assert_equal Rational(1,10),D.point_counterexample[:marginal_switch]
  end
  def test_controlled_opportunity_recovers_attention
    [0,Rational(1,4),Rational(1,2),1].each do |q|
      observed=D.expected_switch(opportunity:Rational(1,2),attention:q)
      assert_equal q,D.recover_attention(observed_switch:observed,known_opportunity:Rational(1,2))
    end
  end
  def test_zero_opportunity_unidentified
    assert_raises(ArgumentError) { D.recover_attention(observed_switch:0,known_opportunity:0) }
  end
  def test_same_lapse_and_response_unidentified
    assert_raises(ArgumentError) { D.recover_attention(observed_switch:Rational(1,10),known_opportunity:Rational(1,2),respond:Rational(1,5),lapse:Rational(1,5)) }
  end
  def test_incompatible_observation
    assert_raises(ArgumentError) { D.recover_attention(observed_switch:1,known_opportunity:Rational(1,2)) }
  end
  def test_full_attention_probability
    assert_equal Rational(1,5),D.expected_switch(opportunity:Rational(1,2),attention:1)
  end
end
