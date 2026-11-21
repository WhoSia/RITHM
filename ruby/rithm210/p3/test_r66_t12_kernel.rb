# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_kernel'
class R66T12KernelTest < Minitest::Test
  S=RithmT12::Schedules
  K=RithmT12::Kernel
  def test_original_cost
    assert_equal [48,27,12,3,0,3,12],(0..6).map { |n| K.route_cost(n) }
  end
  def test_masked_state_conservation
    7.times do |n|
      [0,7,15,42,63].each do |mask|
        row,_=K.masked_row(n,mask)
        assert_equal 1,row.sum
        assert row.all? { |v| v>=0 }
      end
    end
  end
  def test_matching_gross_rates_for_every_n
    rates=[S.common,S.independent,S.fixed_count(3)].map { |s| K.transition(s)[1] }
    assert_equal rates[0],rates[1]
    assert_equal rates[1],rates[2]
  end
  def test_one_period_horizon_unchanged
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      assert_equal 0,K.forecast(n0:4,horizon:1,schedule:s)[:social_cost]
    end
  end
  def test_40_period_mass
    [S.common,S.independent,S.fixed_count(3)].each do |s|
      x=K.forecast(n0:4,horizon:40,schedule:s)
      assert_equal 1,x[:final_occupancy].sum
      assert x[:gross_switches]>=0
    end
  end
  def test_zero_effort_no_change
    x=K.forecast(n0:5,horizon:40,schedule:S.common,effort:0)
    assert_equal 120,x[:congestion]
    assert_equal 0,x[:gross_switches]
  end
  def test_fee_identity
    x=K.forecast(n0:4,horizon:5,schedule:S.fixed_count(3),fee:3)
    assert_equal x[:congestion]+3*x[:gross_switches],x[:social_cost]
  end
end
