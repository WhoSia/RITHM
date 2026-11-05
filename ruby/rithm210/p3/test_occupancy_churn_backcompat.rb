# frozen_string_literal: true
# Regression guard: N-generalized bounds must recover PRE-EXISTING RITHM N=6 result.
require 'minitest/autorun'
require_relative 'occupancy_churn_bounds'
require_relative 'churn_welfare_bounds'
require_relative 'occupancy_equivalence'
class TestOccupancyChurnBackcompat < Minitest::Test
  def test_all_six_person_transitions_agree_with_both_prior_modules
    old=Rithm210ChurnWelfareBounds
    prior=Rithm210OccupancyEquivalence
    current=Rithm210OccupancyChurnBounds
    (0..6).each do |a|
      (0..6).each do |b|
        old_result=old.turnover_bounds(a,b)
        prior_result=prior.sharp_bounds(from:a,to:b)
        new_result=current.gross_range(n:6,a:a,b:b)
        assert_equal old_result[:minimum],new_result[:minimum]
        assert_equal old_result[:maximum],new_result[:maximum]
        assert_equal old_result[:possible],current.possible_gross(n:6,a:a,b:b)
        assert_equal prior_result[:possible],current.possible_gross(n:6,a:a,b:b)
      end
    end
  end
end
