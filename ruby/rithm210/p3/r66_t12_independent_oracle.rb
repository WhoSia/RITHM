# frozen_string_literal: true
require_relative 'r66_t12_kernel'
module RithmT12
  module Oracle
    module_function
    # Enumerates labelled actor-specific flips; NO occupancy binomial convolution.
    def row(n,schedule,effort:Rational(1))
      Kernel.route_cost(n)
      a,b=Kernel.revision_rates(n)
      answer=Array.new(7,Rational(0))
      schedule.each_with_index do |active_prob,active_mask|
        next if active_prob.zero?
        64.times do |flip_mask|
          next unless (flip_mask & ~active_mask).zero?
          prob=active_prob
          6.times do |i|
            next if (active_mask & (1<<i)).zero?
            rate=(i<n ? a : b)*Rational(effort)
            prob*=((flip_mask & (1<<i)).zero? ? 1-rate : rate)
          end
          next if prob.zero?
          next_n=n
          6.times do |i|
            next if (flip_mask & (1<<i)).zero?
            next_n+=(i<n ? -1 : 1)
          end
          answer[next_n]+=prob
        end
      end
      raise 'oracle mass violation' unless answer.sum==1
      answer.freeze
    end
  end
end
