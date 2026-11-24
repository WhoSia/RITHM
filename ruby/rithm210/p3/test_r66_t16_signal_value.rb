# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t16_signal_value'
class T16SignalValueTest < Minitest::Test
  V=RithmT16::SignalValue; B=RithmT16::Belief
  def test_no_value_below_exact_boundary
    [:a,:b].each do |route|
      (0..20).each do |i|
        x=V.evaluate(B.binomial_base,route,persistence:Rational(i,100),base:B.binomial_base)
        assert_equal 0,x[:disclosure_increment]; assert_equal 0,x[:payoff_increment]
      end
      assert_operator V.evaluate(B.binomial_base,route,persistence:Rational(21,100),base:B.binomial_base)[:disclosure_increment],:>,0
    end
  end
  def test_decomposition_and_nonnegative_values
    [:a,:b].each do |route|
      [0,1,2].each do |threshold|
        (0..10).each do |i|
          x=V.evaluate(B.binomial_base,route,persistence:Rational(i,10),base:B.binomial_base,threshold:threshold)
          assert_equal x[:full]-x[:blind],x[:payoff_increment]+x[:disclosure_increment]
          assert_operator x[:payoff_increment],:>=,0; assert_operator x[:disclosure_increment],:>=,0
        end
      end
    end
  end
  def test_degenerate_prior
    x=V.evaluate([0,0,0,0,0,1],:a,persistence:1,base:B.binomial_base)
    assert_equal 4,x[:blind];assert_equal 4,x[:full];assert_equal 0,x[:disclosure_increment]
  end
end
