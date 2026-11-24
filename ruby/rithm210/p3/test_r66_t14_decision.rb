# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t14_kernel'
class R66T14Test < Minitest::Test
  D=RithmT14::Decision;K=RithmT14::Kernel;S=RithmT12::Schedules
  def test_prior_and_conditioning
    assert_equal 1,D.prior.sum
    assert_equal 1,D.posterior(:a).sum
    assert_equal 1,D.posterior(:b).sum
    assert_equal 0,D.posterior(:a)[0]
    assert_equal 0,D.posterior(:b)[6]
    assert_equal Rational(-155,79),D.values(:a)[:net_prior_gain]
    assert_equal Rational(-20,41),D.values(:b)[:net_prior_gain]
  end
  def test_positive_value_below_high_cost
    [:a,:b].each do |route|
      v=D.values(route)[:value_of_information]
      assert_operator v,:>,0;assert_operator v,:<,2
    end
    assert_equal Rational(29,553),D.values(:a)[:value_of_information]
    assert_equal Rational(132,287),D.values(:b)[:value_of_information]
  end
  def test_all_state_baseline_equivalence
    7.times do |n|
      [:a,:b].each do |r|
        x=D.flip_probability(n,r,mechanism: :cognitive)
        assert_equal x,D.flip_probability(n,r,mechanism: :switching)
        assert_equal(D.gain(n,r)>0 ? Rational(1,2) : 0,x)
      end
    end
  end
  def test_interventions_crossed
    assert_equal 1,D.flip_probability(5,:a,mechanism: :cognitive,policy: :free_info)
    assert_equal Rational(1,2),D.flip_probability(5,:a,mechanism: :switching,policy: :free_info)
    assert_equal Rational(1,2),D.flip_probability(5,:a,mechanism: :cognitive,policy: :remove_threshold)
    assert_equal 1,D.flip_probability(5,:a,mechanism: :switching,policy: :remove_threshold)
  end
  def test_all_transition_rows_equal
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      assert_equal K.transition(schedule:s,mechanism: :cognitive),K.transition(schedule:s,mechanism: :switching)
      assert_equal K.transition(schedule:s,mechanism: :cognitive,policy: :free_info),K.transition(schedule:s,mechanism: :switching,policy: :remove_threshold)
    end
  end
  def test_baseline_40_periods_equal
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      a=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :cognitive)
      b=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :switching)
      assert_equal a,b
      assert_equal 1,a[:final].sum
    end
  end
  def test_free_info_does_not_change_switching_cost_model
    s=S.fixed_count(3)
    a=K.forecast(n0:5,horizon:40,schedule:s,mechanism: :switching)
    assert_equal a,K.forecast(n0:5,horizon:40,schedule:s,mechanism: :switching,policy: :free_info)
  end
  def test_unknown_and_negative_inputs
    assert_raises(ArgumentError) { D.values(:a,threshold:-1) }
    assert_raises(ArgumentError) { D.flip_probability(5,:a,mechanism: :other) }
    assert_raises(ArgumentError) { K.forecast(n0:5,horizon:0,schedule:S.common,mechanism: :cognitive) }
  end
end
