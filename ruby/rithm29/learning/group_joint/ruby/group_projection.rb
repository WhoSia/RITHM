# frozen_string_literal: true
require_relative 'directional_joint'
module RithmGroupProjection
  module_function
  def project(joint, previous_a:)
    raise ArgumentError, 'previous_a' unless previous_a.is_a?(Integer) && previous_a.between?(0, 6)
    raise ArgumentError, 'support' unless joint.size == 7 - previous_a && joint.all? { |r| r.size == previous_a + 1 }
    count=Array.new(7,0.0)
    switches=Array.new(7,0.0)
    net=Hash.new(0.0)
    joint.each_with_index do |row,u|
      row.each_with_index do |mass,d|
        raise ArgumentError,'invalid mass' unless mass.is_a?(Numeric) && mass.finite? && mass >= 0
        count[previous_a+u-d]+=mass
        switches[u+d]+=mass
        net[u-d]+=mass
      end
    end
    raise ArgumentError,'normalization' unless (count.sum-1.0).abs < 1e-9
    expected_cost=count.each_with_index.sum { |p,n| p*(4.0+0.5*(n-4)**2) }
    expected_n=count.each_with_index.sum { |p,n| p*n }
    variance_n=count.each_with_index.sum { |p,n| p*(n-expected_n)**2 }
    raise 'welfare mismatch' unless (expected_cost-(4.0+0.5*(variance_n+(expected_n-4)**2))).abs < 1e-9
    {count:count,switches:switches,net:net,expected_cost:expected_cost,mean_a:expected_n,variance_a:variance_n}
  end
  def count_logloss(count_dist, observed)
    raise ArgumentError,'observed' unless observed.is_a?(Integer) && observed.between?(0,6)
    p=count_dist.fetch(observed)
    p<=0 ? Float::INFINITY : -Math.log(p)
  end
  def count_brier(count_dist, observed)
    count_dist.each_with_index.sum { |p,j| (p-(j==observed ? 1.0 : 0.0))**2 }
  end
end
