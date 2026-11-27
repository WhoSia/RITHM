require 'minitest/autorun'
require_relative 'r66_t30_group'
class TestR66T30Group < Minitest::Test
  G=RithmT30::Group
  def test_occupancy_against_all_labelled_combinations
    rng=Random.new(3001)
    100.times do
      ps=Array.new(6){rng.rand};q=G.occupancy(ps);e=Array.new(7,0.0)
      64.times do |mask|
        bits=6.times.map{|j|mask[j]};e[bits.sum]+=bits.zip(ps).reduce(1.0){|v,(b,p)|v*(b==1 ? p : 1-p)}
      end
      q.zip(e).each{|a,b|assert_in_delta a,b,1e-14}
      assert_in_delta 1,q.sum,1e-14
      expected=3*((ps.sum-4)**2+ps.sum{|p|p*(1-p)})
      assert_in_delta expected,G.metrics(ps,[1,1,1,1,0,0])[:predicted_cost],1e-12
    end
  end
  def test_residual_and_guards
    m=G.metrics([0.5]*6,[1]*6);assert_in_delta 0.25,m[:pair_residual],1e-14;assert_equal 12,m[:actual_cost]
    assert_raises(ArgumentError){G.occupancy([0.5]*5)}
    assert_raises(ArgumentError){G.metrics([0.5]*6,[2]*6)}
  end
end
