require 'minitest/autorun'
require_relative 'welfare_temporal_decomposition'
class TestRithm210WelfareTemporalDecomposition < Minitest::Test
  M=Rithm210WelfareTemporalDecomposition
  def rows(a,b)
    [a,b].each_with_index.flat_map do |values,i|
      values.map{|n|{session:i+1,group:1,n:n}}
    end
  end
  def test_all_temporal_variance
    r=M.components(rows([3,5],[4,4]),expected_groups:2,expected_periods:2)
    assert_in_delta 0,r[:mean_bias_loss],1e-12
    assert_in_delta Rational(3,2),r[:within_group_temporal_loss],1e-12
    assert_in_delta 0,r[:between_group_mean_loss],1e-12
    assert_in_delta Rational(3,2),r[:total_excess],1e-12
  end
  def test_all_between_group_variance
    r=M.components(rows([3,3],[5,5]),expected_groups:2,expected_periods:2)
    assert_in_delta 0,r[:within_group_temporal_loss],1e-12
    assert_in_delta 3,r[:between_group_mean_loss],1e-12
    assert_in_delta 3,r[:total_excess],1e-12
  end
  def test_reject_unbalanced_longitudinal_groups
    assert_raises(RuntimeError){M.components(rows([3,4],[4]))}
  end
end
