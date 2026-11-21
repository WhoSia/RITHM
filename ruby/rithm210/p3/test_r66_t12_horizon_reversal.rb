# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_kernel'
class R66T12HorizonTest < Minitest::Test
  K=RithmT12::Kernel
  S=RithmT12::Schedules
  def test_one_step_common_better_at_optimum
    assert_operator K.forecast(n0:4,horizon:2,schedule:S.common)[:congestion],:<,
                    K.forecast(n0:4,horizon:2,schedule:S.independent)[:congestion]
  end
  def test_long_horizon_staggered_better_at_optimum
    a=K.forecast(n0:4,horizon:40,schedule:S.common)
    b=K.forecast(n0:4,horizon:40,schedule:S.independent)
    c=K.forecast(n0:4,horizon:40,schedule:S.fixed_count(3))
    assert_operator c[:congestion],:<,b[:congestion]
    assert_operator b[:congestion],:<,a[:congestion]
    assert_operator c[:gross_switches],:<,b[:gross_switches]
    assert_operator b[:gross_switches],:<,a[:gross_switches]
  end
  def test_long_horizon_staggered_better_at_n5
    a=K.forecast(n0:5,horizon:40,schedule:S.common)
    b=K.forecast(n0:5,horizon:40,schedule:S.independent)
    c=K.forecast(n0:5,horizon:40,schedule:S.fixed_count(3))
    assert_operator c[:congestion],:<,b[:congestion]
    assert_operator b[:congestion],:<,a[:congestion]
  end
  def test_schedule_cost_robust_to_nonnegative_fee
    [0,1,2,10].each do |fee|
      values=[S.common,S.independent,S.fixed_count(3)].map do |s|
        K.forecast(n0:4,horizon:40,schedule:s,fee:fee)[:social_cost]
      end
      assert_operator values[2],:<,values[1]
      assert_operator values[1],:<,values[0]
    end
  end
end
