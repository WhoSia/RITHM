require 'minitest/autorun'
require_relative 'epoch_conditioned_model'
class TestEpochConditionedModel < Minitest::Test
  Q=Rithm210EpochConditionedModel
  def test_empty_epoch_copies_base
    r={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'4','switchWill'=>'0'}
    m=Q.train({[3,1,1,1]=>[r]},{3=>0},0)
    assert_in_delta 0.5,Q.probability(m,r,1,conditional:false),1e-12
    assert_in_delta 0.5,Q.probability(m,r,1,conditional:true),1e-12
  end
  def test_training_only_epoch_shift
    r={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'4','switchWill'=>'1'}
    m=Q.train({[3,1,1,1]=>[r]},{3=>0},1)
    assert_operator Q.probability(m,r,1,conditional:true),:>,Q.probability(m,r,1,conditional:false)
  end
  def test_convolution_mass
    assert_in_delta 1.0,Q.convolve([0.2,0.8,0.4]).sum,1e-12
  end
  def test_joint_equals_count_when_only_one_direction_possible
    j,c=Q.joint_and_count([],[0.4,0.6],1,0)
    assert_in_delta j,c,1e-12
  end
end
