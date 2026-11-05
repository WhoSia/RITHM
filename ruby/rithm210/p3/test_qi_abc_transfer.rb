require 'minitest/autorun'
require_relative 'qi_abc_transfer'
class TestRithm210QiABCTest < Minitest::Test
  Q=Rithm210QiABCTest
  A=Rithm210QiModelATransfer
  def test_model_b_is_nested_in_c
    (0..6).each do |n|
      [0,1].each do |route|
        assert_in_delta Q.probability(:b,[0.4,0.22],route,n),
                        Q.probability(:c,[0.4,0.4,0.22],route,n),1e-12
      end
    end
  end
  def test_a_equal_etas_maps_to_b_only_with_rescaled_theta
    (0..6).each do |n|
      [0,1].each do |route|
        assert_in_delta Q.probability(:a,[0.4,0.4,0.4],route,n),
                        Q.probability(:b,[0.4,0.4*(1-0.4)],route,n),1e-12
      end
    end
  end
  def test_distinct_route_inertia_vs_preference
    n=4
    assert_in_delta 0.4,Q.probability(:c,[0.2,0.6,0.3],1,n),1e-12
    assert_in_delta 0.2,Q.probability(:c,[0.2,0.6,0.3],0,n),1e-12
    assert_operator Q.probability(:a,[0.2,0.6,0.3],1,n),:>,0.4
    assert_operator Q.probability(:a,[0.2,0.6,0.3],0,n),:>,0.2
  end
  def test_fit_and_parameter_boundaries
    cells={[1,3]=>[15,100],[0,3]=>[45,100],[1,5]=>[50,100],[0,5]=>[20,100]}
    [:b,:c,:a].each do |kind|
      fit=Q.fit(kind,cells)
      assert_operator fit[:loss],:<=,Q.neglog(kind,fit[:params],cells)+1e-9
      assert fit[:params][-1].positive?
      assert fit[:params][0...-1].all?{|eta|eta.between?(0,1)}
    end
    assert_raises(ArgumentError){Q.probability(:x,[0.2,0.3],1,4)}
    assert_raises(ArgumentError){Q.probability(:b,[0.2,0.3],1,7)}
    assert_raises(ArgumentError){Q.probability(:c,[0.2,0.5,0.3],2,4)}
    assert_raises(ArgumentError){Q.fit(:b,{})}
  end
  def test_probability_directions_for_high_cost_route
    [:b,:c].each do |kind|
      params=kind==:b ? [0.4,0.3] : [0.2,0.6,0.3]
      assert_operator Q.probability(kind,params,1,6),:>,Q.probability(kind,params,1,0)
      assert_operator Q.probability(kind,params,0,0),:>,Q.probability(kind,params,0,6)
    end
  end
end
