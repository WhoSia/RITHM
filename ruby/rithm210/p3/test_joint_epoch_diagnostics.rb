require 'minitest/autorun'
require_relative 'joint_epoch_diagnostics'
class TestRithm210P3R15JointDiagnostics < Minitest::Test
  M=Rithm210P3R15JointDiagnostics
  def test_convolution_mass_and_expectation
    a=M.convolve([0.1,0.3,0.8])
    assert_equal 4,a.size
    assert_in_delta 1.0,a.sum,1e-12
    assert_in_delta 1.2,a.each_with_index.sum{|p,i|p*i},1e-12
  end
  def test_opposing_switch_cancellation
    rows=[{route:1,y:1,p:0.5},{route:1,y:0,p:0.0},
          {route:1,y:0,p:0.0},{route:1,y:0,p:0.0},
          {route:0,y:1,p:0.5},{route:0,y:0,p:0.0}]
    x=M.group_score({individual:rows,metrics:{predicted_loss:1.5,opposite_route_pair:-1.5}})
    assert_in_delta Math.log(4),x[:joint_logloss],1e-12
    assert_in_delta 0.25,x[:pzero],1e-12
    assert_in_delta 0.25,x[:pcancel],1e-12
    assert_equal 1,x[:observed_cancel]
    assert_in_delta 0.5625,x[:cancel_brier],1e-12
  end
  def test_detect_wrong_welfare_and_empty_rows
    rows=[{route:1,y:0,p:0.5}]*4+[{route:0,y:0,p:0.5}]*2
    assert_raises(RuntimeError){M.group_score({individual:rows,metrics:{predicted_loss:0}})}
    assert_raises(RuntimeError){M.means([])}
  end
end
