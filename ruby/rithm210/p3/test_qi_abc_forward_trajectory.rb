require 'minitest/autorun'
require_relative 'qi_abc_forward_trajectory'
class TestRithm210QiABCForwardTrajectory < Minitest::Test
  M=Rithm210QiABCForwardTrajectory
  def params
    {a:[0.6,0.4,0.4],b:[0.5,0.2],c:[0.6,0.4,0.2]}
  end
  def test_three_qi_markov_kernels_are_stochastic
    [:a,:b,:c].each do |kind|
      [1,10,30,39].each do |t|
        k=M.kernel(kind,params,t)
        assert_equal 7,k.size
        k.each do |row|
          assert_equal 7,row.size
          assert_in_delta 1.0,row.sum,1e-12
          assert row.all?{|v|v>=0 && v<=1}
        end
      end
    end
  end
  def test_first_observation_is_not_replaced_by_model
    [:a,:b,:c].each do |kind|
      (0..6).each do |n|
        x=M.forecast(kind,params,initial:n,horizon:1)
        assert_in_delta Rithm210FiniteHorizonIndependentWelfare.cost(n),
                        x[:expected_total_cost],1e-10
        assert_in_delta 1.0,x[:terminal][n],1e-12
      end
    end
  end
  def test_evolving_expected_welfare_and_terminal_distribution
    [:a,:b,:c].each do |kind|
      x=M.forecast(kind,params,initial:4,horizon:40)
      assert_in_delta 1.0,x[:terminal].sum,1e-9
      assert_operator x[:expected_total_cost],:>=,40*24
      assert_operator x[:expected_total_cost],:<=,40*72
      assert_operator x[:expected_total_cost],:>,40*24
    end
  end
  def test_extract_complete_trajectory_and_reject_discontinuity
    groups={}
    (1..39).each do |t|
      row={'trt'=>'3','NumA'=>'4','NumAnext'=>'4'}
      groups[[5,1,2,t]]=[row]
    end
    x=M.extract_trajectories(groups,[5])
    assert_equal 1,x.size
    assert_equal 40*24,x.first[:observed_total_cost]
    groups[[5,1,2,13]][0]['NumAnext']='5'
    assert_raises(RuntimeError){M.extract_trajectories(groups,[5])}
    groups.delete([5,1,2,13])
    assert_raises(RuntimeError){M.extract_trajectories(groups,[5])}
  end
  def test_invalid_state_guards
    assert_raises(ArgumentError){M.actor_state(1,7)}
    assert_raises(ArgumentError){M.forecast(:a,params,initial:4,horizon:0)}
    assert_raises(ArgumentError){M.propagate([1],Array.new(7){Array.new(7,0.0)})}
  end
end
