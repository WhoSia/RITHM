# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t16_filter'
class T16FilterTest < Minitest::Test
  F=RithmT16::Filter; B=RithmT16::Belief
  def test_history_matters_with_same_last_payoff
    a=F.replay([{route: :a,payoff:14},{route: :a,payoff:9}],persistence:Rational(4,5)).last
    b=F.replay([{route: :a,payoff:0},{route: :a,payoff:9}],persistence:Rational(4,5)).last
    assert_operator a[:next_gain],:<,0
    assert_operator b[:next_gain],:>,0
    refute_equal a[:posterior],b[:posterior]
  end
  def test_no_persistence_erases_history
    a=F.replay([{route: :a,payoff:14},{route: :a,payoff:9}],persistence:0).last
    b=F.replay([{route: :a,payoff:0},{route: :a,payoff:9}],persistence:0).last
    assert_equal a,b
  end
  def test_disclosure_is_past_state_not_next
    a=F.replay([{route: :a,payoff:9,observed_k:5}],persistence:Rational(1,2)).first
    assert_equal [0,0,0,0,0,1],a[:posterior]
    refute_equal a[:posterior],a[:next_prior]
    assert_equal Rational(3,2),a[:next_gain]
  end
  def test_inconsistent_disclosure
    assert_raises(ArgumentError){F.replay([{route: :a,payoff:0,observed_k:0}],persistence:1)}
  end
end
