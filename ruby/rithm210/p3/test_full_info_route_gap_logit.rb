require 'minitest/autorun'
require_relative 'full_info_route_gap_logit'
class TestRithm210FullInfoRouteGapLogit < Minitest::Test
  M=Rithm210FullInfoRouteGapLogit
  def row(n,route,y=0,trt=3,info=1)
    {'trt'=>trt.to_s,'Informed'=>info.to_s,'NumA'=>n.to_s,'RouteA'=>route.to_s,'switchWill'=>y.to_s}
  end
  def test_cost_gap_on_both_routes
    assert_equal(-6.0,M.cost_gap(row(2,1)))
    assert_equal(6.0,M.cost_gap(row(2,0)))
    assert_equal(0.0,M.cost_gap(row(4,1)))
    assert_equal(0.0,M.cost_gap(row(4,0)))
  end
  def test_prohibit_unavailable_cost_info
    assert_raises(ArgumentError){M.cost_gap(row(4,1,0,2,0))}
    assert_raises(ArgumentError){M.cost_gap(row(4,1,0,3,0))}
    assert_raises(ArgumentError){M.cost_gap(row(7,1))}
  end
  def test_logit_monotone_and_route_effect
    a=M.fit_route(Array.new(20){|i|[i-10,i>=10 ? 1 : 0]},ridge:0.1)
    assert_operator a[1],:>,0
    assert_operator M.sigmoid(a[0]+a[1]*5),:>,M.sigmoid(a[0]+a[1]*(-5))
    assert_in_delta 0.5,M.sigmoid(0),1e-12
  end
  def test_constant_training_and_regularization
    a=M.fit_route(Array.new(40){[0.0,0]},ridge:0.01)
    assert_in_delta 0,a[1],1e-12
    assert_operator M.sigmoid(a[0]),:<,0.1
    assert_raises(ArgumentError){M.fit_route([])}
  end
  def test_holdout_session_never_used_in_training
    groups={ [1,1,1,1]=>[row(2,1,1),row(2,0,1)],
             [2,1,1,1]=>[row(2,1,0),row(2,0,0)] }
    m=M.fit(groups,[2])
    all=M.fit(groups,[])
    assert_operator M.probability(m,row(2,1)),:>,M.probability(all,row(2,1))
  end
end
