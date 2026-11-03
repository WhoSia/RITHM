require 'minitest/autorun'
require_relative 'epoch_residual_contrast'
class TestEpochResidualContrast < Minitest::Test
  Q=Rithm210EpochResidualContrast
  def test_one_group_has_no_cross_control
    r=[{session:1,section:1,period:1,group:1,ru:1.0,rd:1.0}]
    assert_equal [],Q.matched(r)
  end
  def test_two_group_exact_contrast
    r=[{session:1,section:1,period:1,group:1,ru:2.0,rd:3.0},
       {session:1,section:1,period:1,group:2,ru:5.0,rd:7.0}]
    m=Q.matched(r)
    assert_equal 2,m.size
    assert_in_delta(-8.0,m[0][:difference],1e-12)
    assert_in_delta(20.0,m[1][:difference],1e-12)
  end
  def test_zero_bootstrap
    r=[{session:1,difference:0.0},{session:2,difference:0.0}]
    t=Q.resample(r,:difference,draws:100)
    assert_equal 0,t[:mean]
    assert_equal 0,t[:lower]
    assert_equal 0,t[:upper]
  end
end
