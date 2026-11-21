# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_pairwise_identity'
class R66T12PairwiseIdentityTest < Minitest::Test
  S=RithmT12::Schedules
  I=RithmT12::PairwiseIdentity
  def test_all_occupancies_exact
    7.times do |n|
      [[S.common,S.independent],[S.fixed_count(3),S.independent],[S.common,S.fixed_count(3)]].each do |a,b|
        assert_equal I.expected_gap(n,a,b),I.direct_one_step(a,n)-I.direct_one_step(b,n)
      end
    end
  end
  def test_initial_4_gap_matches_t5
    assert_equal Rational(-3,5000),I.expected_gap(4,S.common,S.independent)
  end
  def test_initial_5_gap
    assert_equal Rational(117,50),I.expected_gap(5,S.common,S.independent)
  end
  def test_effort_quadratic
    a=S.common;b=S.independent
    assert_equal I.expected_gap(4,a,b)*Rational(1,4),I.expected_gap(4,a,b,effort:Rational(1,2))
  end
  def test_no_marginal_comparability
    assert_raises(ArgumentError) { I.expected_gap(4,S.common(Rational(1,2)),S.common(Rational(2,5))) }
  end
end
