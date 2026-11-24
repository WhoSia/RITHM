# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t14_kernel'
class R66T14DisclosureTest < Minitest::Test
  D=RithmT14::Decision;K=RithmT14::Kernel;S=RithmT12::Schedules
  def test_partial_disclosure_rate
    assert_equal Rational(3,4),D.flip_probability(5,:a,mechanism: :cognitive,policy: :free_info,disclosure:Rational(1,2))
    assert_equal Rational(1,2),D.flip_probability(5,:a,mechanism: :switching,policy: :free_info,disclosure:Rational(1,2))
  end
  def test_zero_disclosure_recovers_baseline
    s=S.common
    assert_equal K.transition(schedule:s,mechanism: :cognitive),K.transition(schedule:s,mechanism: :cognitive,policy: :free_info,disclosure:0)
  end
  def test_closed_class_at_full_disclosure
    p=K.transition(schedule:S.common,mechanism: :cognitive,policy: :free_info)
    assert_equal Rational(1,2),p[0][6]
    assert_equal Rational(1,2),p[6][0]
    assert_equal Rational(1,2),p[5][0]
    assert_equal Rational(1,2),p[5][5]
    assert_equal 0,K.forecast(n0:5,horizon:40,schedule:S.common,mechanism: :cognitive,policy: :free_info)[:final][4]
  end
  def test_reversal_not_restricted_to_full_disclosure
    s=S.common
    a=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive)
    b=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive,policy: :free_info,disclosure:Rational(1,2))
    assert_operator b[:congestion],:>,a[:congestion]
  end
  def test_invalid_disclosure
    assert_raises(ArgumentError){ D.flip_probability(5,:a,mechanism: :cognitive,policy: :free_info,disclosure:2) }
  end
end
