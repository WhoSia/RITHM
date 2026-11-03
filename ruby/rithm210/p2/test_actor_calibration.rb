require 'minitest/autorun'
require_relative 'actor_calibration'
class TestRithm210ActorCalibration < Minitest::Test
  Q=Rithm210ActorCalibration
  def test_epoch_partition
    assert_equal :early,Q.epoch(1)
    assert_equal :early,Q.epoch(10)
    assert_equal :middle,Q.epoch(11)
    assert_equal :middle,Q.epoch(29)
    assert_equal :late,Q.epoch(30)
    assert_equal :late,Q.epoch(39)
  end
end
