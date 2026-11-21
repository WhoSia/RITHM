# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_counterexamples'
class T13CounterexamplesTest < Minitest::Test
  C=RithmT13::Counterexamples
  def test_baseline_fixed_three_wins
    assert_equal [:fixed_three,:independent,:common],C.order(C.cell(attention:1,threshold:0))
  end
  def test_half_attention_zero_threshold_fixed_wins
    assert_equal [:fixed_three,:independent,:common],C.order(C.cell(attention:Rational(1,2),threshold:0))
  end
  def test_half_attention_private_threshold_two_reverses
    assert_equal [:common,:independent,:fixed_three],C.order(C.cell(attention:Rational(1,2),threshold:2))
  end
  def test_no_attention_common_wins
    assert_equal [:common,:independent,:fixed_three],C.order(C.cell(attention:0))
  end
  def test_high_threshold_common_wins
    assert_equal [:common,:independent,:fixed_three],C.order(C.cell(attention:1,threshold:5))
  end
  def test_fee_counts_resources_separately
    a=C.cell(attention:Rational(1,2),threshold:2,fee:0)
    b=C.cell(attention:Rational(1,2),threshold:2,fee:2)
    a.each_key do |policy|
      assert_equal a[policy][:congestion],b[policy][:congestion]
      assert_equal a[policy][:congestion]+2*a[policy][:gross_switches],b[policy][:social_cost]
    end
  end
  def test_no_private_original_data
    assert_equal false,C.public_summary[:original_subject_data_included]
  end
end
