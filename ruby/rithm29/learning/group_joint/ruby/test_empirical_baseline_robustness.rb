require 'minitest/autorun'
require_relative 'empirical_baseline_robustness'
class RobustnessTest < Minitest::Test
 def test_unequal_weighting
  rows=[{n:1,'global'=>{joint:1.0},'conditional'=>{joint:0.0}},
        {n:3,'global'=>{joint:1.0},'conditional'=>{joint:2.0}}]
  r=RithmBaselineRobustness.interval(rows,:joint,draws:200)
  assert_in_delta 0.0,r[:equal_session][:point],1e-12
  assert_in_delta 0.5,r[:transition_weighted][:point],1e-12
 end
 def test_determinism
  rows=Array.new(24){ {n:117,'global'=>{count:2.0},'conditional'=>{count:1.0}} }
  a=RithmBaselineRobustness.interval(rows,:count,draws:200)
  assert_equal a,RithmBaselineRobustness.interval(rows,:count,draws:200)
  assert_in_delta(-1,a[:equal_session][:point],1e-12)
 end
end
