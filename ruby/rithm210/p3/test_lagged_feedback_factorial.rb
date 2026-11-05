require 'minitest/autorun'
require_relative 'lagged_feedback_factorial'
class TestRithm210LaggedFeedbackFactorial < Minitest::Test
  M=Rithm210LaggedFeedbackFactorial
  S=Rithm210SmoothSignalClock
  def test_non_degenerate_truthful_signal_age_factorial
    x=M.factorial(mask:15,previous_n:2,strength:0.3,tremble:0.1)
    assert_equal 4,x[:outcomes].size
    assert_in_delta 4.9050836974,x[:outcomes][[:lagged,false]][:excess],1e-8
    assert_in_delta 2.5540527304,x[:outcomes][[:lagged,true]][:excess],1e-8
    assert_in_delta 5.5950406282,x[:outcomes][[:current,false]][:excess],1e-8
    assert_in_delta 2.8822157651,x[:outcomes][[:current,true]][:excess],1e-8
    assert_in_delta(-0.3617938962,x[:interaction],1e-8)
  end
  def test_current_initial_information_matches_prior_sequential_protocol
    [false,true].each do |feedback|
      x=M.transition(15,previous_n:4,initial_report: :current,within_round_refresh:feedback)
      y=S.transition(15,clock: :sequential,signal:(feedback ? :refreshed : :frozen),strength:0.3,tremble:0.1)
      (x.keys|y.keys).each{|state|assert_in_delta x.fetch(state,0),y.fetch(state,0),1e-12}
    end
  end
  def test_identical_past_current_signal_has_no_age_effect
    x=M.factorial(mask:15,previous_n:4)
    assert_in_delta 0,x[:initial_fresh_effect_without_feedback],1e-12
    assert_in_delta 0,x[:interaction],1e-12
  end
  def test_reject_out_of_domain_and_fake_report_types
    assert_raises(ArgumentError){M.transition(15,previous_n:-1,initial_report: :lagged,within_round_refresh:false)}
    assert_raises(ArgumentError){M.transition(15,previous_n:2,initial_report: :fabricated,within_round_refresh:false)}
    assert_raises(ArgumentError){M.transition(15,previous_n:2,initial_report: :lagged,within_round_refresh:0)}
  end
end
