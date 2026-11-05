# frozen_string_literal: true
require 'minitest/autorun'
require_relative 'occupancy_churn_bounds'
class TestOccupancyChurnBounds < Minitest::Test
  B=Rithm210OccupancyChurnBounds
  def test_exhaustive_realizability_and_sharp_bounds
    (1..8).each do |n|
      (0..n).each do |a|
        (0..n).each do |b|
          observed=[]
          (0...(1<<n)).each do |bits|
            next unless bits.to_s(2).count('1')==b
            u=(a...n).count { |i| bits[i]==1 }
            d=(0...a).count { |i| bits[i]==0 }
            observed<<{u:u,d:d}
          end
          expected=B.possible_pairs(n:n,a:a,b:b)
          assert_equal expected,observed.uniq.sort_by{|z|z[:d]},"n=#{n} a=#{a} b=#{b}"
          gross=observed.map{|z|z[:u]+z[:d]}.uniq.sort
          assert_equal gross,B.possible_gross(n:n,a:a,b:b)
          assert_equal({minimum:gross.min,maximum:gross.max},B.gross_range(n:n,a:a,b:b))
          assert gross.all?{|g|(g-b+a).even?}
        end
      end
    end
  end
  def test_optimal_occupancy_masks_zero_to_four_switches
    assert_equal [0,2,4],B.possible_gross(n:6,a:4,b:4)
    assert_equal 24,B.congestion_cost(4)
    assert_equal({min_gross:0,max_gross:12,min_switch_cost:0,max_switch_cost:Rational(12,5)},
      B.resource_bounds(n:6,path:[4,4,4,4],k:Rational(1,5)))
  end
  def test_fixed_occupancy_path_cannot_identify_resource_switch_cost
    assert_equal({min_gross:2,max_gross:10,min_switch_cost:2,max_switch_cost:10},
      B.resource_bounds(n:6,path:[4,3,4],k:1))
  end
  def test_reject_invalid_inputs
    assert_raises(ArgumentError){B.gross_range(n:6,a:-1,b:1)}
    assert_raises(ArgumentError){B.possible_pairs(n:0,a:0,b:0)}
    assert_raises(ArgumentError){B.resource_bounds(n:6,path:[4],k:1)}
    assert_raises(ArgumentError){B.resource_bounds(n:6,path:[4,4],k:-1)}
    assert_raises(ArgumentError){B.resource_bounds(n:6,path:[4,4],k:Float::INFINITY)}
    assert_raises(ArgumentError){B.resource_bounds(n:6,path:[4,4],k:Float::NAN)}
    assert_raises(ArgumentError){B.resource_bounds(n:6,path:[4,4],k:Complex(1,0))}
    assert_equal Rational(4,3),B.resource_bounds(n:6,path:[4,4],k:Rational(1,3))[:max_switch_cost]
  end
end
