# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'history_features'

class TestHistoryFeatures < Minitest::Test
  def rows
    [{period: 1, route_a: 1, num_a: 5, cost: 5},
     {period: 2, route_a: 0, num_a: 4, cost: 4},
     {period: 3, route_a: 0, num_a: 4, cost: 4},
     {period: 4, route_a: 1, num_a: 3, cost: 3}]
  end

  def test_no_future_leakage
    assert_equal RithmLearning.features(rows.first(3)),
                 RithmLearning.features(rows).first(2)
  end

  def test_experience_and_switches
    f = RithmLearning.features(rows)
    assert_equal [1, 1, 2], f.map { |v| v[:familiarity] }
    assert_equal [1, 0, 1], f.map { |v| v[:switched] }
    assert_equal 1, f[1][:prior_switch_rate]
    assert_equal 0, f[2][:previous_relative_cost]
    assert_equal 1, f[0][:route_state_familiarity]
    assert_equal 5.0, f[0][:previous_mean_cost]
  end

  def test_bad_route_rejected
    assert_raises(ArgumentError) do
      RithmLearning.features([{period: 1, route_a: 2, num_a: 0, cost: 0}])
    end
  end
end
