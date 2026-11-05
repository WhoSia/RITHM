require 'minitest/autorun'
require_relative 'r19_persistent_q_filter'
class TestRithm210R19PersistentQFilter < Minitest::Test
  M=Rithm210R19PersistentQFilter
  S=Rithm210R19SSMExact
  def test_uniform_initial_and_persistent_bayesian_update
    f=M::Filter.new(qmax:3,lapse:0.02)
    h=S.blank_history
    assert_in_delta 0.5,f.predict(history:h,informed:true),1e-12
    assert_equal [1.0/3]*3,f.update(route_a:true)
    h[:paired_differences].concat([10,10,-20])
    assert f.predict(history:h,informed:true).between?(0,1)
    a=f.update(route_a:true)
    assert_in_delta 1,a.sum,1e-12
    refute_equal [1.0/3]*3,a
  end
  def test_prohibit_future_choice_and_invalid_parameters
    f=M::Filter.new(qmax:2,lapse:0.02)
    assert_raises(RuntimeError){f.update(route_a:true)}
    assert_raises(ArgumentError){M::Filter.new(qmax:0)}
    assert_raises(ArgumentError){M::Filter.new(lapse:-0.1)}
    f.predict(history:S.blank_history,informed:false)
    assert_raises(RuntimeError){f.predict(history:S.blank_history,informed:false)}
    f.update(route_a:false)
    assert_in_delta 1,f.weights.sum,1e-12
  end
  def test_q1_reduces_to_lapsed_ssm
    f=M::Filter.new(qmax:1,lapse:0.04)
    h=S.blank_history
    h[:paired_differences]<<10
    assert_in_delta 0.98,f.predict(history:h,informed:true),1e-12
    assert_equal [1.0],f.update(route_a:false)
  end
end
