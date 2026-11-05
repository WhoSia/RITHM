require 'minitest/autorun'
require_relative 'r19_ssm_session_contrast'
class TestRithm210R19SSMSessionContrast < Minitest::Test
  M=Rithm210R19SSMSessionContrast
  def rows
    (1..4).flat_map{|s|[
      {session:s,treatment:3,informed:true,model:'ssm_2',n:40,brier:0.3+s/100.0},
      {session:s,treatment:3,informed:true,model:'own_route_frequency',n:40,brier:0.2+s/100.0}]}
  end
  def test_paired_bootstrap
    a=M.compare(rows,treatment:3,informed:true,model:'ssm_2',draws:500)
    assert_equal 4,a[:sessions]
    assert_in_delta 0.1,a[:mean_brier_difference],1e-12
    assert_in_delta 0.1,a[:bootstrap_percentile95][0],1e-12
    assert_in_delta 0.1,a[:bootstrap_percentile95][1],1e-12
    assert_equal 4,a[:sessions_ssm_worse]
  end
  def test_missing_pairs_and_n_not_silently_accepted
    x=rows.reject{|r|r[:session]==4&&r[:model]=='ssm_2'}
    assert_raises(ArgumentError){M.compare(x,treatment:3,informed:true,model:'ssm_2')}
    y=rows;y[0][:n]=3
    assert_raises(ArgumentError){M.compare(y,treatment:3,informed:true,model:'ssm_2')}
  end
end
