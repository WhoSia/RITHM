# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'route_cost_court'
class TestRouteCostCourt < Minitest::Test
  M=RouteCostCourt
  def test_explicit_strict_rank_reversal
    r=M.assess([0,0,1],[0,0,0],[1,0,0])
    assert_equal 1,r.fetch('better_hamming')
    assert_equal 2,r.fetch('worse_hamming')
    assert_equal 4,r.fetch('better_cost_error')
    assert_equal 0,r.fetch('worse_cost_error')
    assert r.fetch('cost_rank_reversed')
  end
  def test_exact_three_person_census
    r=M.census(3)
    assert_equal 176,r.fetch('compared_strict_pairs')
    assert_equal 36,r.fetch('rank_reversals')
    assert_equal 104,r.fetch('tied_cost_errors')
    assert_equal false,r.fetch('causal_effect_identified')
  end
  def test_permutation_and_flip_symmetry
    [0,0,1,1].permutation.to_a.uniq.each do |v|
      assert_equal M.congestion(v), M.congestion(v.reverse)
      assert_equal M.congestion(v), M.congestion(v.map{|x|1-x})
    end
  end
  def test_lipschitz_bound_of_predicted_cost
    M.vectors(4).each do |a|
      M.vectors(4).each do |b|
        assert_operator((M.congestion(a)-M.congestion(b)).abs,:<=,6*M.mismatch(a,b))
      end
    end
  end
  def test_invalid_input_is_rejected
    assert_raises(ArgumentError){M.congestion([0,2])}
    assert_raises(ArgumentError){M.assess([0,1],[0],[1,1])}
  end
end
