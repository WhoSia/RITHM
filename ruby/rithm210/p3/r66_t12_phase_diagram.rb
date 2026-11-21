# frozen_string_literal: true
require_relative 'r66_t12_kernel'
module RithmT12
  module PhaseDiagram
    module_function
    def trajectories(n0:,max_horizon:40,effort:Rational(1))
      Kernel.route_cost(n0)
      raise ArgumentError,'max horizon 2..1000' unless max_horizon.is_a?(Integer) && max_horizon.between?(2,1000)
      schedules={common:Schedules.common,independent:Schedules.independent,
                 staggered_three:Schedules.fixed_count(3)}
      schedules.transform_values do |schedule|
        p,sw=Kernel.transition(schedule,effort)
        dist=Array.new(7,Rational(0));dist[n0]=Rational(1)
        congestion=Rational(0);flips=Rational(0)
        (1..max_horizon).map do |h|
          congestion+=7.times.sum(Rational(0)) { |n| dist[n]*Kernel.route_cost(n) }
          record={horizon:h,congestion:congestion,revisions:flips}
          if h<max_horizon
            flips+=7.times.sum(Rational(0)) { |n| dist[n]*sw[n] }
            dist=7.times.map { |m| 7.times.sum(Rational(0)) { |n| dist[n]*p[n][m] } }
          end
          record
        end
      end
    end
    def crossover(trajectory,first,second)
      raise ArgumentError,'unknown policy name' unless trajectory.key?(first) && trajectory.key?(second)
      pairs=trajectory[first].zip(trajectory[second])
      positive=pairs.select { |a,b| a[:congestion]>b[:congestion] }
      negative=pairs.select { |a,b| a[:congestion]<b[:congestion] }
      {first_positive_horizon:positive.first&.first&.fetch(:horizon),
       first_negative_horizon:negative.first&.first&.fetch(:horizon)}
    end
    def fee_indifference(a,b)
      dc=a[:congestion]-b[:congestion]
      ds=a[:revisions]-b[:revisions]
      ds.zero? ? nil : -dc/ds
    end
  end
end
