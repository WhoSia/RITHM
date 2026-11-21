# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t13_kernel'
class T13OffEquilibriumAttentionTest < Minitest::Test
  S=RithmT12::Schedules;K=RithmT13::Kernel
  def outputs(q)
    {common:S.common,independent:S.independent,fixed_three:S.fixed_count(3)}.transform_values do |s|
      K.total(n0:5,horizon:40,schedule:s,attention:q,threshold:0,lapse:0)[:congestion]
    end
  end
  def test_nonzero_dynamics_without_errors
    assert outputs(Rational(1,2)).values.all? { |c| c>0 }
  end
  def test_more_attention_common_clock_increases_cost
    assert_operator outputs(1)[:common],:>,outputs(Rational(1,2))[:common]
  end
  def test_more_attention_independent_decreases_cost
    assert_operator outputs(1)[:independent],:<,outputs(Rational(1,2))[:independent]
  end
  def test_more_attention_staggered_decreases_cost
    assert_operator outputs(1)[:fixed_three],:<,outputs(Rational(1,2))[:fixed_three]
  end
  def test_staggered_wins_from_five_with_zero_errors
    [Rational(1,2),1].each do |q|
      v=outputs(q)
      assert_operator v[:fixed_three],:<,v[:independent]
      assert_operator v[:independent],:<,v[:common]
    end
  end
end
