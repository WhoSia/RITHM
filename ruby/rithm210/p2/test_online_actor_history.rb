require 'minitest/autorun'
require_relative 'online_actor_history'

class TestRithm210OnlineActorHistory < Minitest::Test
  M=Rithm210OnlineIdentity

  def test_no_history_equals_prior
    assert_in_delta 0.3,M.online_probability(0.3,[0,0],20.0),1e-12
  end

  def test_prior_only_updates_from_past
    assert_in_delta 0.3,M.online_probability(0.3,[0,0],20.0),1e-12
    assert_in_delta 7.0/21,M.online_probability(0.3,[1,1],20.0),1e-12
    assert_in_delta 6.0/21,M.online_probability(0.3,[0,1],20.0),1e-12
  end

  def test_illegal_prior_strength_rejected
    assert_raises(ArgumentError){M.online_probability(0.3,[1,1],0.0)}
  end

  def test_joint_convolution_normalization
    assert_in_delta 1.0,M.convolve([0.2,0.5,0.8]).sum,1e-12
  end

  def test_single_direction_joint_equals_next_count
    r={'RouteA'=>'0','switchBtoAWill'=>'1','switchAtoBWill'=>'0'}
    joint,count,cross=M.group_scores([r],[0.4])
    assert_in_delta(-Math.log(0.4),joint,1e-12)
    assert_in_delta joint,count,1e-12
    assert_in_delta 0.0,cross,1e-12
  end
end
