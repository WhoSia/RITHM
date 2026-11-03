require 'minitest/autorun'
require_relative 'nested_gamma_cv'
class TestRithm210NestedGammaCV < Minitest::Test
  M=Rithm210NestedGammaCV
  def test_split_every_session_once
    f=M.split((1..24).to_a,6)
    assert_equal 24,f.length
    assert_equal [4,4,4,4,4,4],(0..5).map{|i|f.values.count(i)}
  end
  def test_train_only_frequency
    r={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'4','switchWill'=>'1'}
    groups={[1,1,1,1]=>[r],[2,1,1,1]=>[r]}
    fit=M.train_model(groups,[1])
    assert_equal [1,1],fit[0].fetch(Rithm210LatentCV.key(r))
    assert_in_delta (1+20*(2.0/3))/(1+20),M.probability(fit,r),1e-12
  end
  def test_unobserved_actor_defaults_to_half
    r={'trt'=>'1','Informed'=>'0','RouteA'=>'1','Cost'=>'4'}
    assert_in_delta 0.5,M.probability([{},{}],r),1e-12
  end
end
