# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t16_belief'
class T16BeliefTest < Minitest::Test
  B=RithmT16::Belief
  def test_route_gain_and_consistency
    6.times { |k| assert_equal 3*k-11,B.gain(k,:a); assert_equal 11-3*k,B.gain(k,:b) }
    assert_equal 1,B.binomial_base.sum
  end
  def test_signal_ambiguity
    assert_equal [1,1,1,1,1,1].map { |x| Rational(x,6) },B.posterior([1]*6,:a,9)
    assert_equal [0,0,0,0,0,1],B.posterior([1]*6,:b,14)
    assert_equal [0,0,0,0,0,1],B.posterior([1]*6,:a,0)
  end
  def test_prior_matters
    assert_equal B.binomial_base,B.posterior(B.binomial_base,:a,9)
  end
  def test_prediction_endpoints
    p=B.posterior([1]*6,:b,14)
    assert_equal p,B.predict(p,persistence:1,base:B.binomial_base)
    assert_equal B.binomial_base,B.predict(p,persistence:0,base:B.binomial_base)
  end
  def test_information_value
    p=[1]*6
    [:a,:b].each do |route|
      assert_equal 0,B.previous_state_information_value(p,route,persistence:0,base:B.binomial_base)
      assert_operator B.previous_state_information_value(p,route,persistence:1,base:B.binomial_base),:>,0
      (0..10).each do |i|
        assert_operator B.previous_state_information_value(p,route,persistence:Rational(i,10),base:B.binomial_base),:>=,0
      end
    end
  end
  def test_impossible_signal
    assert_raises(ArgumentError){B.posterior([1]*6,:a,99)}
    assert_raises(ArgumentError){B.predict([1]*6,persistence:2,base:[1]*6)}
  end
end
