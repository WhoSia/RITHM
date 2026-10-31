# frozen_string_literal: true
require 'csv'
require_relative 'directional_joint'
require_relative 'group_projection'
module RithmGroupScoring
  module_function
  def evaluate(previous:, probability_a:, observed_a:)
    raise ArgumentError, 'exactly six actors required' unless previous.length==6 && probability_a.length==6 && observed_a.length==6
    raise ArgumentError, 'invalid observed route' unless observed_a.all? { |a| a==0 || a==1 }
    joint=RithmDirectionalJoint.distribution(previous:previous,probabilities:probability_a)
    projected=RithmGroupProjection.project(joint,previous_a:previous.sum)
    observed_n=observed_a.sum
    observed_u=(0...6).count { |i| previous[i]==0 && observed_a[i]==1 }
    observed_d=(0...6).count { |i| previous[i]==1 && observed_a[i]==0 }
    p_ud=RithmDirectionalJoint.probability(joint,observed_u,observed_d)
    {
      joint_logloss:p_ud>0 ? -Math.log(p_ud) : Float::INFINITY,
      count_logloss:RithmGroupProjection.count_logloss(projected[:count],observed_n),
      count_brier:RithmGroupProjection.count_brier(projected[:count],observed_n),
      expected_cost:projected[:expected_cost],
      realized_cost:4.0+0.5*(observed_n-4)**2,
      forecast_switchers:RithmDirectionalJoint.expectation(joint)[:gross],
      actual_switchers:observed_u+observed_d,
      cancellation_probability:RithmDirectionalJoint.expectation(joint)[:cancellation],
      actual_cancellation:observed_u>0 && observed_d>0 ? 1 : 0
    }
  end
end
