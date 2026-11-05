require 'minitest/autorun'
require_relative 'pairwise_source_audit'
class TestRithm210PairwiseSourceAudit < Minitest::Test
  M=Rithm210PairwiseSourceAudit
  W=Rithm210PairwiseWelfare
  def synthetic_rows
    (1..24).flat_map do |s|
      [{session:s,epoch: :early,**W.decompose(up:1,down:0)},
       {session:s,epoch: :late,**W.decompose(up:0,down:0)}]
    end
  end
  def test_exact_contribution_decomposition
    sessions=(1..24).to_a
    totals=M.session_totals(sessions,synthetic_rows)
    stats=M.summary(totals,sessions)
    changes=M.contrasts(stats)
    assert_in_delta 3,changes[:cost_decline],1e-12
    assert_in_delta 3,changes[:gross_component],1e-12
    assert_in_delta 0,changes[:pair_component],1e-12
  end
  def test_missing_session_by_epoch_keeps_zero_count
    sessions=(1..24).to_a
    rows=synthetic_rows.reject{|r|r[:session]==1 && r[:epoch]==:early}
    totals=M.session_totals(sessions,rows)
    stats=M.summary(totals,sessions)
    assert_equal 23,stats[:early][:n]
    assert_equal 24,stats[:late][:n]
    assert_raises(RuntimeError){M.summary(totals,[1])}
  end
  def test_gross_switch_reduction_can_have_offsetting_pair_change
    rows=[
      {session:1,epoch: :early,**W.decompose(up:1,down:1)},
      {session:1,epoch: :late,**W.decompose(up:0,down:0)}]
    stats=M.summary(M.session_totals([1],rows),[1])
    c=M.contrasts(stats)
    assert_equal 0,c[:cost_decline]
    assert_equal 6,c[:gross_component]
    assert_equal(-6,c[:pair_component])
  end
end
