require 'minitest/autorun'
require_relative 'group_scoring'
class GroupScoringTest < Minitest::Test
  def test_perfect_forecast
    before=[1,1,1,1,0,0]
    after=before.dup
    out=RithmGroupScoring.evaluate(previous:before,probability_a:after.map(&:to_f),observed_a:after)
    assert_in_delta 0.0,out[:joint_logloss],1e-12
    assert_in_delta 0.0,out[:count_brier],1e-12
    assert_in_delta 4.0,out[:expected_cost],1e-12
    assert_equal 0,out[:actual_switchers]
  end
  def test_uniform
    before=[1,1,1,1,0,0]
    after=[0,1,1,1,1,0]
    out=RithmGroupScoring.evaluate(previous:before,probability_a:Array.new(6,0.5),observed_a:after)
    assert_in_delta 5.25,out[:expected_cost],1e-12
    assert_in_delta 4.0,out[:realized_cost],1e-12
    assert_in_delta 3.0,out[:forecast_switchers],1e-12
    assert_equal 2,out[:actual_switchers]
  end
end
