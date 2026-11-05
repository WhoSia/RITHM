require 'minitest/autorun'
require_relative 'occupancy_equivalence'
class TestRithm210OccupancyEquivalence < Minitest::Test
  M=Rithm210OccupancyEquivalence
  def test_all_49_occupancy_pairs_have_sharp_feasible_bounds
    (0..6).each do |a|
      (0..6).each do |b|
        possibilities=M.feasible_turnovers(from:a,to:b)
        assert_operator possibilities.size,:>=,1
        assert_equal possibilities.map{|x|x[:gross]}.min,M.sharp_bounds(from:a,to:b)[:minimum]
        assert_equal possibilities.map{|x|x[:gross]}.max,M.sharp_bounds(from:a,to:b)[:maximum]
        assert_equal (b-a).abs,possibilities.first[:gross]
        possibilities.each do |r|
          prior=[1]*a+[0]*(6-a)
          new_choice=M.construct(previous:prior,up:r[:up],down:r[:down])
          assert_equal b,new_choice.sum
          assert_equal r[:gross],new_choice.each_index.count{|i|prior[i]!=new_choice[i]}
        end
      end
    end
  end
  def test_same_occupancy_and_same_congestion_allow_distinct_gross_movement
    assert M.same_cost_but_different_switches?
    assert_equal [0,2,4],M.sharp_bounds(from:4,to:4)[:possible]
    assert_equal [0,2,4,6],M.sharp_bounds(from:3,to:3)[:possible]
  end
  def test_sharp_path_bounds_with_identical_congestion_cost_path
    r=M.path_bounds([4,4,4,4])
    assert_equal 0,r[:minimum]
    assert_equal 12,r[:maximum]
    assert_equal 3,r[:periods]
  end
  def test_invalid_domain
    assert_raises(ArgumentError){M.feasible_turnovers(from:-1,to:4)}
    assert_raises(ArgumentError){M.construct(previous:[1],up:0,down:0)}
    assert_raises(ArgumentError){M.path_bounds([4])}
  end
end
