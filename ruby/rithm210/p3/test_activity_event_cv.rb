require 'minitest/autorun'
require_relative 'activity_event_cv'
class TestRithm210ActivityEventCV < Minitest::Test
  M=Rithm210ActivityEventCV
  def test_no_switch_and_cancellation_separated
    people=[{'RouteA'=>'1'},{'RouteA'=>'0'}]
    r=M.event_probabilities(people,[0.5,0.5])
    assert_in_delta 0.25,r[:none],1e-12
    assert_in_delta 0.25,r[:cancel],1e-12
    assert_in_delta 28.5,r[:next_loss],1e-12
  end
  def test_all_zero_switch_probabilities
    people=[{'RouteA'=>'1'},{'RouteA'=>'0'}]
    r=M.event_probabilities(people,[0.0,0.0])
    assert_equal 1,r[:none]
    assert_equal 0,r[:cancel]
  end
  def test_binary_proper_scores
    assert_in_delta 0.25,M.binary_score(0.5,1)[:brier],1e-12
    assert_in_delta Math.log(2),M.binary_score(0.5,0)[:logloss],1e-12
  end
end
