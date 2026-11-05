require 'minitest/autorun'
require_relative 'smooth_signal_clock'
class TestRithm210SmoothSignalClock < Minitest::Test
  M=Rithm210SmoothSignalClock
  def test_zero_strength_and_domain
    assert_in_delta 0.5,M.probability(true,4,actor:0,strength:0,tremble:0.1,biases:[0.0]*6,shock:0),1e-12
    assert_raises(ArgumentError){M.transition(15,clock: :simultaneous,signal: :frozen,strength:-1)}
    assert_raises(ArgumentError){M.transition(15,clock: :simultaneous,signal: :frozen,shock_amplitude:-1)}
    assert_raises(ArgumentError){M.transition(15,clock: :simultaneous,signal: :frozen,biases:[0]*5)}
  end
  def test_frozen_clock_same_complete_labelled_law_under_individual_heterogeneity
    [0,15,30,63].each do |mask|
      params={strength:0.7,tremble:0.1,biases:[2,-1,0.5,-0.5,1,0],shock_amplitude:1.5}
      a=M.transition(mask,clock: :simultaneous,signal: :frozen,**params)
      b=M.transition(mask,clock: :sequential,signal: :frozen,**params)
      assert_in_delta 1.0,a.values.sum,1e-11
      (a.keys|b.keys).each{|s|assert_in_delta a.fetch(s,0),b.fetch(s,0),1e-11}
    end
  end
  def test_smooth_one_round_sign_reversal
    first=M.factorial(mask:0,strength:0.05,tremble:0.1)
    second=M.factorial(mask:15,strength:0.05,tremble:0.1)
    assert_in_delta 0.2571582576,first[:interaction],1e-8
    assert_in_delta(-0.97811787,second[:interaction],1e-8)
    assert_operator first[:interaction],:>,0
    assert_operator second[:interaction],:<,0
  end
  def test_actor_identity_breaks_seven_state_lumpability
    a=M.lumpability_witness(mask_a:15,mask_b:30,biases:[2,0,0,0,0,0],strength:0.7,tremble:0.1)
    b=M.lumpability_witness(mask_a:15,mask_b:30,strength:0.7,tremble:0.1)
    assert_operator a[:total_variation],:>,0.25
    assert_in_delta 0,b[:total_variation],1e-12
  end
end
