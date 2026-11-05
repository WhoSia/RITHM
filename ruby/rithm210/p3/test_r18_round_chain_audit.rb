require 'minitest/autorun'
require_relative 'r18_round_chain_audit'
class TestRithm210R18RoundChainAudit < Minitest::Test
  M=Rithm210R18RoundChainAudit
  A=Rithm210R18TruthfulSignalAudit
  def valid(protocol=:lagged_feedback)
    age,feedback=M::PROTOCOLS.fetch(protocol)
    previous=3; current=15
    rounds=(1..40).map do |t|
      info=A.example(previous_mask:previous,initial_mask:current,
        report_age:age,feedback:feedback)
      ending=A.check_round(**info).fetch(:final_mask)
      record={period:t,previous_mask:previous,initial_mask:current,
              protocol:protocol,events:info.fetch(:events)}
      previous,current=current,ending
      record
    end
    {protocol:protocol,baseline_previous_mask:3,baseline_current_mask:15,
      baseline_timestamp:100,assignment_timestamp:101,rounds:rounds}
  end
  def test_all_four_protocols_and_40round_cost_identity
    M::PROTOCOLS.keys.each do |protocol|
      x=M.verify(**valid(protocol))
      assert_equal 40,x[:rounds]
      assert_equal 240,x[:opportunities]
      assert_equal x[:cumulative_cost]-960,x[:cumulative_excess]
      assert x[:complete]
    end
  end
  def test_reject_broken_previous_and_current_history
    x=valid;x[:rounds][1][:previous_mask]=0
    assert_raises(ArgumentError){M.verify(**x)}
    x=valid;x[:rounds][1][:initial_mask]=0
    assert_raises(ArgumentError){M.verify(**x)}
  end
  def test_baseline_must_precede_randomization_and_protocol_stays_fixed
    x=valid;x[:baseline_timestamp]=x[:assignment_timestamp]
    assert_raises(ArgumentError){M.verify(**x)}
    x=valid;x[:rounds][12][:protocol]=:current_feedback
    assert_raises(ArgumentError){M.verify(**x)}
  end
  def test_exact_horizon_and_truthful_feedback
    x=valid;x[:rounds].pop
    assert_raises(ArgumentError){M.verify(**x)}
    x=valid;x[:rounds][0][:events][1][:shown_n]=99
    assert_raises(ArgumentError){M.verify(**x)}
  end
end
