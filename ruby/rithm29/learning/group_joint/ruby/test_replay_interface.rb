# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'group_scoring'
class ReplayInterfaceTest < Minitest::Test
 def test_score_returns_cancellation_values
   p=[0.2,0.4,0.6,0.8,0.3,0.7];old=[1,1,1,0,0,0];now=[0,1,1,1,0,0]
   out=RithmGroupScoring.evaluate(previous:old,probability_a:p,observed_a:now)
   assert out.key?(:cancellation_probability)
   assert out.key?(:actual_cancellation)
   assert_equal 1,out[:actual_cancellation]
   assert out[:cancellation_probability].between?(0.0,1.0)
   assert_in_delta 4.0,out[:realized_cost],1e-12
 end
end
