require 'minitest/autorun'
require_relative 'update_clock_sensitivity'
class TestRithm210UpdateClockSensitivity < Minitest::Test
  M=Rithm210UpdateClockSensitivity
  def test_full_grid_and_boundaries
    x=M.run
    assert_equal 56,x[:grid_points]
    assert_equal 0,x[:positive]
    assert_equal 8,x[:zero]
    assert_equal 48,x[:negative]
    assert_equal(-48.to_r,x[:min][:interaction])
  end
  def test_n4_known_values_and_zero_tremble
    a=M.run(grid:[0.to_r,Rational(1,10),Rational(1,2)])[:initial4]
    assert_equal 3,a.size
    assert_equal 0,a[0][:interaction]
    assert_in_delta(-1.1102016,a[1][:interaction].to_f,1e-12)
    assert_equal 0,a[2][:interaction]
  end
  def test_empty_grid_rejected
    assert_raises(ArgumentError){M.run(grid:[])}
  end
end
