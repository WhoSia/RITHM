require 'minitest/autorun'
require_relative 'update_clock_signal_factorial'
class TestRithm210UpdateClockSignalFactorial < Minitest::Test
  M=Rithm210UpdateClockSignalFactorial
  def test_four_protocols_normalized_and_quadratic
    x=M.factorial
    assert_equal 4,x[:protocols].size
    x[:protocols].each_value do |a|
      assert_equal 1,a[:distribution].sum
      assert_equal 7,a[:distribution].length
      assert a[:distribution].all?{|p|p>=0}
      assert_equal a[:expected_excess],3*(a[:variance]+(a[:mean]-4)**2)
    end
  end
  def test_six_opportunities_frozen_order_invariance
    [0,3,15,31,63].each do |mask|
      [0,2,4,6].each do |old_n|
        a=M.switch_distribution(mask,clock: :simultaneous,signal: :frozen,observed_n:old_n)
        b=M.switch_distribution(mask,clock: :sequential,signal: :frozen,observed_n:old_n)
        assert_equal a,b
      end
    end
  end
  def test_signal_updates_change_exact_welfare
    x=M.factorial(initial_mask:15)
    assert_equal Rational(87,50),x[:protocols][[:simultaneous,:frozen]][:expected_excess]
    assert_equal Rational(87,50),x[:protocols][[:sequential,:frozen]][:expected_excess]
    assert_in_delta 0.6297984,x[:protocols][[:sequential,:refreshed]][:expected_excess].to_f,1e-12
    assert_in_delta(-1.1102016,x[:difference_in_differences].to_f,1e-12)
  end
  def test_zero_tremble_equilibrium
    x=M.factorial(initial_mask:15,tremble:0.to_r)
    x[:protocols].each_value do |r|
      assert_equal 4,r[:mean]
      assert_equal 0,r[:expected_excess]
    end
  end
  def test_reject_bad_parameters
    assert_raises(ArgumentError){M.occupancy(64)}
    assert_raises(ArgumentError){M.switch_distribution(15,clock: :mixed,signal: :frozen)}
    assert_raises(ArgumentError){M.switch_distribution(15,clock: :simultaneous,signal: :old)}
    assert_raises(ArgumentError){M.switch_distribution(15,clock: :sequential,signal: :frozen,observed_n:7)}
    assert_raises(ArgumentError){M.move_probability(true,4,tremble:Rational(3,4))}
  end
end
