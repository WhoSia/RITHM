require 'minitest/autorun'
require_relative 'r18_truthful_signal_audit'
class TestRithm210R18TruthfulSignalAudit < Minitest::Test
  M=Rithm210R18TruthfulSignalAudit
  def test_valid_examples_for_all_four_arms
    [:lagged,:current].each do |age|
      [false,true].each do |feed|
        trace=M.example(report_age:age,feedback:feed)
        output=M.check_round(**trace)
        assert_equal 6,output[:opportunities]
        assert_equal true,output[:trace_valid]
      end
    end
  end
  def test_reject_a_future_report_disguised_as_previous
    x=M.example(report_age: :lagged,feedback:false)
    x[:events][0][:shown_n]=4
    assert_raises(ArgumentError){M.check_round(**x)}
  end
  def test_reject_missing_opportunity_and_duplicate_participant
    x=M.example
    x[:events].pop
    assert_raises(ArgumentError){M.check_round(**x)}
    x=M.example
    x[:events][5][:actor]=x[:events][0][:actor]
    assert_raises(ArgumentError){M.check_round(**x)}
  end
  def test_reject_illegal_other_person_switch_and_wrong_prestate
    x=M.example
    x[:events][0][:after_mask]=x[:events][0][:before_mask]^(1<<2)
    assert_raises(ArgumentError){M.check_round(**x)}
    x=M.example
    x[:events][1][:before_mask]=0
    assert_raises(ArgumentError){M.check_round(**x)}
  end
  def test_reject_missing_microfeedback_and_false_timestamp
    x=M.example(report_age: :lagged,feedback:true)
    x[:events][1][:report_stamp]=:previous_period
    assert_raises(ArgumentError){M.check_round(**x)}
    x=M.example(report_age: :lagged,feedback:true)
    x[:events][2][:shown_n]=0
    assert_raises(ArgumentError){M.check_round(**x)}
  end
  def test_history_equals_current_sends_equal_numeric_initial_signals_but_distinct_age
    x=M.example(previous_mask:15,initial_mask:15,report_age: :lagged,feedback:false)
    y=M.example(previous_mask:15,initial_mask:15,report_age: :current,feedback:false)
    assert_equal x[:events][0][:shown_n],y[:events][0][:shown_n]
    refute_equal x[:events][0][:report_stamp],y[:events][0][:report_stamp]
    assert M.check_round(**x)[:trace_valid]
    assert M.check_round(**y)[:trace_valid]
  end
end
