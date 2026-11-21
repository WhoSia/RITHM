# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'r66_t12_activation_grid'
class R66T12ActivationGridTest < Minitest::Test
  G=RithmT12::ActivationGrid
  def test_fixed_pair_covariance_all_k
    G.grid.each do |c|
      k=c[:k]
      assert_equal -Rational(k*(6-k),180),c[:expected_pair_cov_fixed]
    end
  end
  def test_five_distinct_marginal_opportunity_regimes
    assert_equal [Rational(1,6),Rational(1,3),Rational(1,2),Rational(2,3),Rational(5,6)],G.grid.map { |c| c[:theta] }
  end
  def test_40_period_staggered_dominance_in_this_toy_grid
    G.grid.each do |c|
      p=c[:policies]
      assert_operator p[:fixed][:congestion],:<,p[:independent][:congestion]
      assert_operator p[:independent][:congestion],:<,p[:common][:congestion]
    end
  end
  def test_invalid_k
    assert_raises(ArgumentError) { G.cell(0) }
    assert_raises(ArgumentError) { G.cell(6) }
  end
end
