require 'minitest/autorun'
require_relative 'stratified_contrasts'
class TestRithm210StratifiedContrasts < Minitest::Test
  Q=Rithm210StratifiedContrasts
  def test_mean_delta
    assert_in_delta 0.5,Q.average([{joint1:2.0,joint0:1.0},{joint1:1.0,joint0:1.0}]),1e-12
  end
  def test_paired_treatment_epoch_interaction
    rows=[]
    (1..2).each do |s|
      (1..3).each do |trt|
        %w[early middle late].each do |ep|
          delta=trt==3 && ep=='early' ? -0.2 : 0.0
          rows<<{session:s,treatment:trt,epoch:ep,joint1:1.0+delta,joint0:1.0}
        end
      end
    end
    result=Q.construct(rows)
    assert_equal 2,result.size
    assert_in_delta(-0.2,result[0][:interaction_full_no_early_late],1e-12)
    assert_in_delta(-0.2,result[1][:interaction_full_no_early_late],1e-12)
  end
  def test_interval_constant
    rows=[{x:-0.2},{x:-0.2},{x:-0.2}]
    out=Q.interval(rows,:x,draws:100)
    assert_in_delta(-0.2,out[:point],1e-12)
    assert_in_delta(-0.2,out[:lower],1e-12)
    assert_in_delta(-0.2,out[:upper],1e-12)
  end
end
