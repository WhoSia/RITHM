# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'friction_court'
class TestP19FrictionCourt < Minitest::Test
  M=Rithm29P19
  F=M::Friction.new(read_compute:1.to_r,switching:Rational(1,2),mismatch:2.to_r)
  def test_all_horizon_attained_witness
    [1,2,3,17].each do |t|
      w=M.stationary_witness(t)
      assert_equal Rational(11*t,2),w.fetch(:social_cost)
      assert_equal :attained_lower_bound_only,w.fetch(:kind)
    end
  end
  def test_constant_future_additivity
    x=[Rational(3,4),Rational(1,4),0.to_r]
    future=M::STATES.to_h{|s|[s,[7.to_r,7.to_r]]}
    a=M.verify([0,0],x,x,F)
    b=M.verify([0,0],x,x,F,future:future)
    assert a[:nash] && b[:nash]
    assert_equal a[:values].map{|v|v+7},b[:values]
  end
  def test_invalid_inputs_rejected
    assert_raises(ArgumentError){M.cost_matrix([0,0],M::Friction.new(read_compute:-1.to_r,switching:0.to_r,mismatch:0.to_r))}
    assert_raises(ArgumentError){M.verify([0,0],[1.to_r,0.to_r,0.to_r],[1.to_r,0.to_r],F)}
  end
  def test_nonconstant_continuation_affects_deviations
    x=[1.to_r,0.to_r,0.to_r]
    future=M::STATES.to_h{|s|[s,[s.sum.to_r,0.to_r]]}
    a=M.verify([0,0],x,x,F)
    b=M.verify([0,0],x,x,F,future:future)
    refute_equal a[:deviation_costs],b[:deviation_costs]
  end
end
