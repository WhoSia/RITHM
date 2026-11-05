require 'minitest/autorun'
require_relative 'qi_model_a_transfer'
class TestRithm210QiModelATransfer < Minitest::Test
  M=Rithm210QiModelATransfer
  def row(route,n,sw)
    {'trt'=>'3','Informed'=>'1','RouteA'=>route.to_s,'NumA'=>n.to_s,'switchWill'=>sw.to_s}
  end
  def test_equal_cost_and_equal_attractions
    pars=[0.2,0.2,0.5]
    assert_in_delta 0.4,M.switch_probability(pars,1,4),1e-12
    assert_in_delta 0.4,M.switch_probability(pars,0,4),1e-12
  end
  def test_low_sensitivity_half_reconsideration
    x=M.switch_probability([0.25,0.50,1e-8],1,4)
    y=M.switch_probability([0.25,0.50,1e-8],0,4)
    assert_in_delta 0.375,x,1e-6
    assert_in_delta 0.25,y,1e-6
  end
  def test_invalid_parameters
    assert_raises(ArgumentError){M.switch_probability([-1,0.2,0.2],1,4)}
    assert_raises(ArgumentError){M.switch_probability([0.2,0.2,0.0],1,4)}
    assert_raises(ArgumentError){M.switch_probability([0.2,0.2,0.2],2,4)}
  end
  def test_training_sessions_are_excluded
    g={[1,1,1,1]=>[row(1,4,1),row(0,4,1)],
       [2,1,1,1]=>[row(1,4,0),row(0,4,0)]}
    a=M.counts(g,[2]);b=M.counts(g,[1])
    assert_equal [1,1],a[[1,4]]
    assert_equal [0,1],b[[1,4]]
  end
  def test_fit_improves_likelihood_and_stays_in_bounds
    c={ [1,4]=>[10,100],[0,4]=>[50,100],
        [1,5]=>[25,100],[0,5]=>[40,100] }
    x=M.fit(c)
    assert_operator x[:loss],:<,M.loss([0.5,0.5,0.5],c)
    assert x[:params][0].between?(0,1)
    assert x[:params][1].between?(0,1)
    assert_operator x[:params][2],:>,0
  end
end
