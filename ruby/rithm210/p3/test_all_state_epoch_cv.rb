require 'minitest/autorun'
require_relative 'all_state_epoch_cv'
class TestRithm210AllStateEpochCV < Minitest::Test
  M=Rithm210AllStateEpochCV
  def person(route,y:0,n:4,next_n:4)
    {'RouteA'=>route.to_s,'switchAtoBWill'=>(route==1 ? y : 0).to_s,
     'switchBtoAWill'=>(route==0 ? y : 0).to_s,'NumA'=>n.to_s,'NumAnext'=>next_n.to_s}
  end
  def test_all_seven_occupancies_deterministically_hold
    (0..6).each do |n|
      people=Array.new(n){person(1,n:n,next_n:n)}+Array.new(6-n){person(0,n:n,next_n:n)}
      r=M.group_score(people,Array.new(6,0.0))
      assert_equal 0.0,r[:joint]
      assert_in_delta 3*(n-4)**2,r[:forecast_excess],1e-10
      assert_in_delta r[:actual_excess],r[:forecast_excess],1e-10
    end
  end
  def test_opposing_cancellation_at_n4
    people=Array.new(4){person(1)}+Array.new(2){person(0)}
    people[0]['switchAtoBWill']='1'
    people[4]['switchBtoAWill']='1'
    result=M.group_score(people,[0.5,0,0,0,0.5,0])
    assert_in_delta Math.log(4),result[:joint],1e-12
    assert_in_delta 0.25,result[:cancel_pred],1e-12
    assert_equal 1.0,result[:cancel_actual]
  end
  def test_reject_bad_occupancy_and_probability
    people=Array.new(4){person(1)}+Array.new(2){person(0)}
    assert_raises(RuntimeError){M.group_score(people,[-0.1,0,0,0,0,0])}
    people[0]['NumAnext']='3'
    assert_raises(RuntimeError){M.group_score(people,Array.new(6,0.1))}
  end
  def test_convolution_mass_and_extremes
    assert_in_delta 1.0,M.convolve([0.2,0.8,0.4]).sum,1e-12
    assert_equal [1.0],M.convolve([])
    assert_equal [0.0,0.0,1.0],M.convolve([1.0,1.0])
  end
end
