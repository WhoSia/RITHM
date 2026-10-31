# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'directional_joint'
class DirectionalJointTest < Minitest::Test
  def test_boundary
    j=RithmDirectionalJoint.distribution(previous:Array.new(6,1),probabilities:Array.new(6,.5))
    assert_equal 1,j.size
    assert_equal 7,j[0].size
    assert_in_delta 0,RithmDirectionalJoint.expectation(j)[:cancellation],1e-12
  end
  def test_exact_enumeration
    (0..6).each do |n|
      prev=Array.new(n,1)+Array.new(6-n,0)
      p=Array.new(6) { |i| (i+1)/8.0 }
      joint=RithmDirectionalJoint.distribution(previous:prev,probabilities:p)
      enumerated=Array.new(7-n) { Array.new(n+1,0.0) }
      64.times do |mask|
        outcomes=(0...6).map { |i| (mask>>i)&1 }
        prob=outcomes.each_with_index.reduce(1.0) { |a,(x,i)| a*(x==1 ? p[i] : 1-p[i]) }
        u=(0...6).count { |i| prev[i]==0 && outcomes[i]==1 }
        d=(0...6).count { |i| prev[i]==1 && outcomes[i]==0 }
        enumerated[u][d]+=prob
      end
      joint.each_with_index { |row,u| row.each_with_index { |v,d| assert_in_delta enumerated[u][d],v,1e-12 } }
    end
  end
  def test_nontrivial_cancel
    j=RithmDirectionalJoint.distribution(previous:[1,0],probabilities:[.5,.5])
    assert_in_delta .25,RithmDirectionalJoint.expectation(j)[:cancellation],1e-12
  end
  def test_invalid_input
    assert_raises(ArgumentError) { RithmDirectionalJoint.distribution(previous:[1],probabilities:[1.5]) }
  end
end
