require 'minitest/autorun'
require_relative 'online_history_shock'

class TestRithm210OnlineHistoryShock < Minitest::Test
  M=Rithm210OnlineHistoryShock

  def test_zero_shock_reduces_to_independent_bernoulli
    row={'RouteA'=>'0','switchBtoAWill'=>'1','switchAtoBWill'=>'0'}
    j,c=M.group_scores([row],[0.4],0.0)
    assert_in_delta(-Math.log(0.4),j,1e-12)
    assert_in_delta j,c,1e-12
  end

  def test_shift_inverse_symmetry
    p=0.5
    assert_in_delta 1.0,M.shifted(p,0.3)+M.shifted(p,-0.3),1e-12
  end

  def test_group_probability_stays_finite
    people=[
      {'RouteA'=>'1','switchBtoAWill'=>'0','switchAtoBWill'=>'1'},
      {'RouteA'=>'0','switchBtoAWill'=>'1','switchAtoBWill'=>'0'}
    ]
    [0.0,0.15,0.30,0.45].each do |gamma|
      j,c=M.group_scores(people,[0.3,0.6],gamma)
      assert j.finite? && j>=0
      assert c.finite? && c>=0
    end
  end
end
