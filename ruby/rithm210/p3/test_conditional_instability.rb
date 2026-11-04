require 'minitest/autorun'
require_relative 'conditional_instability'

class TestRithm210ConditionalInstability < Minitest::Test
  M=Rithm210ConditionalInstability
  D=Rithm210TurnoverWelfareDrift

  def test_exact_given_optimal_current_occupancy
    rows=[D.score(4,0,0),D.score(4,1,1),D.score(4,1,0)]
    a=M.aggregate(rows)
    assert_equal 3,a[:n]
    assert_in_delta 1.0,a[:expected_next_loss],1e-12
    assert_in_delta 2.0/3,a[:net_move_zero],1e-12
    assert_in_delta 1.0/3,a[:gross_switch_zero],1e-12
    assert_in_delta 1.0/3,a[:cancellation],1e-12
  end

  def test_conditioned_epoch
    rows=[{treatment:3,epoch: :early,**D.score(4,1,0)},
          {treatment:3,epoch: :late,**D.score(4,0,0)}]
    x=M.conditional_by_epoch(rows,trt:3,n:4)
    assert_equal 3,x[:early][:expected_next_loss]
    assert_equal 0,x[:late][:expected_next_loss]
  end

  def test_cluster_bootstrap_with_missing_session_epoch_cells
    rows=(1..24).map do |session|
      early=session.odd?
      {session:session,treatment:3,epoch:early ? :early : :late,
        **D.score(4,early ? 1 : 0,0)}
    end
    result=M.paired_bootstrap(rows,draws:1000)
    assert_in_delta 3,result[:next_loss_decline][:point],1e-12
    assert_in_delta 3,result[:next_loss_decline][:lower],1e-12
    assert_in_delta(-1,result[:net_zero_early_minus_late][:point],1e-12)
    assert_in_delta(-1,result[:gross_zero_early_minus_late][:point],1e-12)
    assert_in_delta 0,result[:cancellation_early_minus_late][:point],1e-12
  end
end
