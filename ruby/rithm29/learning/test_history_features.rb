# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'history_features'

class TestHistoryFeatures < Minitest::Test
  def rows
    [{period: 1, route_a: 1, num_a: 5, cost: 5, payoff: 7},
     {period: 2, route_a: 0, num_a: 4, cost: 4, payoff: 9},
     {period: 3, route_a: 0, num_a: 4, cost: 4, payoff: 6},
     {period: 4, route_a: 1, num_a: 3, cost: 3, payoff: 8}]
  end

  def test_no_future_leakage
    [true, false].each do |type|
      assert_equal RithmLearning.features(rows.first(3), informed: type),
                   RithmLearning.features(rows, informed: type).first(2)
    end
  end

  def test_informed_experience
    f = RithmLearning.features(rows, informed: true)
    assert_equal [1, 1, 2], f.map { |v| v[:familiarity] }
    assert_equal [1, 0, 1], f.map { |v| v[:switched] }
    assert_equal 1, f[1][:prior_switch_rate]
    assert_equal 0, f[2][:previous_relative_cost]
    assert_equal 5.0, f[0][:previous_mean_feedback]
  end

  def test_uninformed_never_reads_hidden_congestion
    rows_without_hidden = rows.map { |v| v.reject { |k, _| [:num_a, :cost].include?(k) } }
    u = RithmLearning.features(rows_without_hidden, informed: false)
    assert_equal RithmLearning.features(rows, informed: false), u
    assert_equal :received_payoff, u.first[:feedback_kind]
    assert_equal 7.0, u.first[:previous_mean_feedback]
    refute u.first.key?(:previous_n)
    refute u.first.key?(:previous_relative_cost)
    refute u.first.key?(:familiarity)
    refute u.first.key?(:route_state_familiarity)
  end

  def test_missing_payoff_for_uninformed_rejected
    assert_raises(KeyError) { RithmLearning.features(rows.map { |v| v.reject { |k, _| k == :payoff } }, informed: false) }
  end

  def test_bad_route_rejected
    assert_raises(ArgumentError) { RithmLearning.features([{period: 1, route_a: 2, num_a: 0, cost: 0}]) }
  end
end
