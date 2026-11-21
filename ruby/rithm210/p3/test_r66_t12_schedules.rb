# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_schedules'
class R66T12SchedulesTest < Minitest::Test
  S=RithmT12::Schedules
  def test_distribution_normalized
    [S.common,S.independent,S.fixed_count(3)].each { |w| assert_equal 1,w.sum }
  end
  def test_actor_marginals_identical
    [S.common,S.independent,S.fixed_count(3)].each { |w| 6.times { |i| assert_equal Rational(1,2),S.marginal(w,i) } }
  end
  def test_pairwise_covariance_differs
    assert_equal Rational(1,4),S.covariance(S.common,0,1)
    assert_equal Rational(0),S.covariance(S.independent,0,1)
    assert_equal Rational(-1,20),S.covariance(S.fixed_count(3),0,1)
  end
  def test_fixed_count_preserves_exact_three
    w=S.fixed_count(3)
    assert_equal 20,w.count(&:positive?)
    assert_equal 1,w.each_with_index.sum(Rational(0)) { |p,m| S.popcount(m)==3 ? p : 0 }
  end
  def test_extreme_schedules_match
    assert_equal S.common(0),S.independent(0)
    assert_equal S.common(1),S.independent(1)
    assert_equal S.fixed_count(0),S.common(0)
    assert_equal S.fixed_count(6),S.common(1)
  end
  def test_reject_outside_interval
    assert_raises(ArgumentError) { S.common(Rational(3,2)) }
    assert_raises(ArgumentError) { S.independent(-1) }
    assert_raises(ArgumentError) { S.fixed_count(7) }
  end
  def test_reject_invalid_distribution
    assert_raises(ArgumentError) { S.validate([1]) }
  end
end
