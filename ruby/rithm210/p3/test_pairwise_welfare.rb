require 'minitest/autorun'
require_relative 'pairwise_welfare'
class TestRithm210PairwiseWelfare < Minitest::Test
  M=Rithm210PairwiseWelfare
  def test_exhaust_all_seven_occupancies_and_feasible_turnovers
    checked=0
    (0..6).each do |n|
      (0..6-n).each do |u|
        (0..n).each do |d|
          r=M.decompose(up:u,down:d,current_a:n)
          assert_equal (u-d)**2,r[:gross]+2*r[:pair_balance]
          assert_equal 3*(n+u-d-4)**2,r[:next_loss]
          assert_equal r[:next_loss]-3*(n-4)**2,r[:loss_change]
          checked+=1
        end
      end
    end
    assert_equal 84,checked
  end
  def test_cancelling_opposing_changes_cost_not_occupancy
    r=M.decompose(up:1,down:1)
    assert_equal 2,r[:gross]
    assert_equal(-1,r[:pair_balance])
    assert_equal 0,r[:next_loss]
  end
  def test_same_direction_changes_are_costly_at_optimum
    r=M.decompose(up:2,down:0)
    assert_equal 2,r[:gross]
    assert_equal 1,r[:same_direction_pairs]
    assert_equal 12,r[:next_loss]
  end
  def test_mean_identity_and_invalid_parameters
    a=[M.decompose(up:0,down:0),M.decompose(up:1,down:1),
      M.decompose(up:2,down:0)]
    r=M.mean_moments(a)
    assert_in_delta r[:squared_net],r[:gross]+2*r[:pair_balance],1e-12
    assert_raises(ArgumentError){M.decompose(up:3,down:0)}
    assert_raises(ArgumentError){M.mean_moments([])}
  end
end
