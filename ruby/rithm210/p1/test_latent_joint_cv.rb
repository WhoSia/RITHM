require 'minitest/autorun'
require_relative 'latent_joint_cv'
class TestLatentJointCV < Minitest::Test
 Q=Rithm210LatentCV
 def test_zero_shock_exactly_independent_convolution
  a=[0.2,0.5];b=[0.3]
  j,c=Q.joint_and_count(a,b,1,1,0.0)
  assert_in_delta(-Math.log(0.3*0.5),j,1e-12)
  assert_in_delta(-Math.log(0.43),c,1e-12)
 end
 def test_joint_positive_and_symmetric_sign
  a=[0.2,0.4];b=[0.3]
  assert_equal Q.joint_and_count(a,b,1,1,0.4),Q.joint_and_count(a,b,1,1,-0.4)
 end
 def test_logit_probability
  assert_in_delta 0.5,Q.logit_shift(0.5,0),1e-12
  assert_operator Q.logit_shift(0.5,0.5),:>,0.5
 end
end
