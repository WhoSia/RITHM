# frozen_string_literal: true
require_relative 'r66_t12_kernel'
module RithmT12
  module ActivationGrid
    module_function
    def cell(k,initial:4,horizon:40)
      raise ArgumentError,'integer k 1..5' unless k.is_a?(Integer) && k.between?(1,5)
      theta=Rational(k,6)
      policies={common:Schedules.common(theta),independent:Schedules.independent(theta),
                fixed:Schedules.fixed_count(k)}
      policies.each_value do |weights|
        6.times { |actor| raise 'marginal mismatch' unless Schedules.marginal(weights,actor)==theta }
      end
      joint={common:theta,independent:theta**2,fixed:Rational(k*(k-1),30)}
      joint.each do |key,value|
        raise 'pair joint invalid' unless Schedules.pair_joint(policies.fetch(key),0,1)==value
      end
      {k:k,theta:theta,expected_pair_cov_fixed:-Rational(k*(6-k),180),
       policies:policies.transform_values { |weights| Kernel.forecast(n0:initial,horizon:horizon,schedule:weights) }}
    end
    def grid(initial:4,horizon:40)
      (1..5).map { |k| cell(k,initial:initial,horizon:horizon) }
    end
  end
end
