require 'minitest/autorun'
require_relative 'churn_welfare_bounds'

class TestRithm210ChurnWelfareBounds < Minitest::Test
  M=Rithm210ChurnWelfareBounds
  def test_sharp_bounds_for_every_current_next_occupancy
    (0..6).each do |n|
      (0..6).each do |m|
        actual=(0..(6-n)).flat_map do |u|
          (0..n).map{|d|u+d if n+u-d==m}
        end.compact.sort.uniq
        assert_equal actual,M.turnover_bounds(n,m)[:possible]
      end
    end
  end
  def test_identical_occupancies_have_different_possible_real_costs
    assert_equal [0,2,4],M.turnover_bounds(4,4)[:possible]
    [0,1,2].each do |k|
      r=M.exact_record(n:4,u:k,d:k,theta:Rational(1,2))
      assert_equal 0,r[:congestion]
      assert_equal k,r[:observed_turnover_welfare]
      assert_equal 0,r[:occupancy_identified_lower]
      assert_equal 2,r[:occupancy_identified_upper]
    end
  end
  def test_unseen_opposing_turnover
    r=M.exact_record(n:3,u:2,d:1,theta:1)
    assert_equal 3,r[:gross]
    assert_equal 2,r[:hidden_cancellation_churn]
    assert_equal 1,r[:occupancy_identified_lower]
  end
  def test_invalid_real_resource_cost
    assert_raises(ArgumentError){M.exact_record(n:4,u:0,d:0,theta:-1)}
  end
end
