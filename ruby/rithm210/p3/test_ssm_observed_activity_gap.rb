require 'minitest/autorun'
require_relative 'ssm_observed_activity_gap'
class TestRithm210SSMObservedActivityGap < Minitest::Test
  M=Rithm210SSMObservedActivityGap
  def fixture
    (1..24).to_h{|s|[s,{early:[1,0],late:[1,1]}]}
  end
  def test_gap_and_cluster_interval
    x=M.compare(fixture,sim_early:0.6,sim_late:0.5,draws:100)
    assert_in_delta 1.0,x[:observed_change],1e-12
    assert_in_delta 1.1,x[:gap],1e-12
    assert_in_delta 1.1,x[:percentile95].first,1e-12
  end
  def test_zero_count_cells_do_not_become_zero_outcomes
    x=fixture
    x[1][:early]=[0,0]
    y=M.rates(x,(1..24).to_a)
    assert_equal 23,y[:early][:n]
    assert_equal 24,y[:late][:n]
    assert_raises(RuntimeError){M.rates(x,[1])}
  end
  def test_repeated_seed_deterministic
    a=M.compare(fixture,sim_early:0.6,sim_late:0.5,draws:100)
    assert_equal a,M.compare(fixture,sim_early:0.6,sim_late:0.5,draws:100)
  end
end
