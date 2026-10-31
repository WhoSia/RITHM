# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'group_projection'
class GroupProjectionTest < Minitest::Test
  def test_exhaustive_deterministic_transitions
    (0...64).each do |pm|
      previous=(0...6).map { |i| (pm>>i)&1 }
      (0...64).each do |nm|
        following=(0...6).map { |i| (nm>>i)&1 }
        joint=RithmDirectionalJoint.distribution(previous:previous,probabilities:following.map(&:to_f))
        projection=RithmGroupProjection.project(joint,previous_a:previous.sum)
        assert_in_delta 1.0,projection[:count][following.sum],1e-12
        assert_in_delta 1.0,projection[:switches][previous.zip(following).count { |x,y| x!=y }],1e-12
        assert_in_delta 4.0+0.5*(following.sum-4)**2,projection[:expected_cost],1e-12
      end
    end
  end
  def test_uniform_bernoulli
    previous=[1,1,1,1,0,0]
    joint=RithmDirectionalJoint.distribution(previous:previous,probabilities:Array.new(6,0.5))
    projection=RithmGroupProjection.project(joint,previous_a:4)
    factorial=->(n) { (1..n).reduce(1,:*) }
    (0..6).each { |k| assert_in_delta factorial.call(6).to_f/(factorial.call(k)*factorial.call(6-k))/64,projection[:count][k],1e-12 }
    assert_in_delta 5.25,projection[:expected_cost],1e-12
    assert_in_delta 1.5,projection[:variance_a],1e-12
  end
  def test_invalid
    assert_raises(ArgumentError) { RithmGroupProjection.project([[1.0]],previous_a:4) }
  end
end
