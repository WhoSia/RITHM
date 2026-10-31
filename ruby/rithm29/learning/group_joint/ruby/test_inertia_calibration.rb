require 'minitest/autorun'
require_relative 'inertia_calibration'
class InertiaCalibrationTest < Minitest::Test
  def test_zero_identity
    (0..20).each do |j|
      p = j / 20.0
      [0,1].each { |old| assert_equal p,RithmInertiaCalibration.adjusted_probability(p,old,0.0) }
    end
  end
  def test_monotone_switch_reduction
    [0.01,0.2,0.5,0.8,0.99].each do |p|
      [0,1].each do |old|
        a=RithmInertiaCalibration.switch_probability(p,old,0)
        b=RithmInertiaCalibration.switch_probability(p,old,1.0)
        assert_operator b,:<,a
      end
    end
  end
  def test_extreme_probabilities
    [0.0,1.0].each do |p|
      [0,1].each { |old| assert_equal p,RithmInertiaCalibration.adjusted_probability(p,old,500.0) }
    end
  end
  def test_invalid
    assert_raises(ArgumentError) { RithmInertiaCalibration.adjusted_probability(0.5,2,1) }
    assert_raises(ArgumentError) { RithmInertiaCalibration.adjusted_probability(0.5,1,-1) }
    assert_raises(ArgumentError) { RithmInertiaCalibration.adjusted_probability(Float::NAN,1,1) }
  end
end
