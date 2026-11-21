# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_kernel'
class T13MechanismsTest < Minitest::Test
  M=RithmT13::Mechanisms;K=RithmT13::Kernel;S=RithmT12::Schedules
  def test_own_gain_both_routes
    assert_equal [-2,-1],[M.private_gain(4,:a),M.private_gain(4,:b)]
    assert_equal [1,-4],[M.private_gain(5,:a),M.private_gain(5,:b)]
  end
  def test_distinct_attention_and_private_threshold
    assert_equal Rational(1,50),M.rate(gain:1,attention:0)
    assert_equal Rational(2,5),M.rate(gain:1,attention:1,threshold:0)
    assert_equal Rational(1,50),M.rate(gain:1,attention:1,threshold:1)
  end
  def test_threshold_not_counted_as_real_fee
    b=K.total(n0:5,horizon:4,schedule:S.independent,threshold:2,real_resource_fee:0)
    c=K.total(n0:5,horizon:4,schedule:S.independent,threshold:2,real_resource_fee:3)
    assert_equal b[:congestion],c[:congestion]
    assert_equal b[:social_cost]+3*b[:gross_switches],c[:social_cost]
  end
  def test_attention_zero_valid_all_schedules
    [S.common,S.independent,S.fixed_count(3)].each do |w|
      p,_=K.transitions(schedule:w,attention:0)
      assert_equal 7,p.length
      assert p.all? { |row| row.sum==1 }
    end
  end
  def test_exact_t12_baseline
    require_relative 'r66_t12_kernel'
    [S.common,S.independent,S.fixed_count(3)].each do |w|
      a=K.total(n0:4,schedule:w)
      b=RithmT12::Kernel.forecast(n0:4,horizon:40,schedule:w)
      assert_equal b[:congestion],a[:congestion]
      assert_equal b[:gross_switches],a[:gross_switches]
    end
  end
  def test_invalid_probabilities
    assert_raises(ArgumentError){M.rate(gain:1,attention:Rational(4,3))}
    assert_raises(ArgumentError){M.rate(gain:1,threshold:-1)}
    assert_raises(ArgumentError){K.total(n0:5,horizon:4,schedule:S.common,real_resource_fee:-1)}
  end
end
