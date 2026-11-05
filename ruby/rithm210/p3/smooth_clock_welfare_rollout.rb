# frozen_string_literal: true
# R17E: autonomous 40-step occupancy-level rollout only for exchangeable actors.
require_relative 'smooth_signal_clock'
module Rithm210SmoothClockWelfareRollout
  module_function
  S=Rithm210SmoothSignalClock
  def kernel(clock:,signal:,strength:,tremble:0.1,shock_amplitude:0.0,biases:Array.new(6,0.0))
    raise ArgumentError,'persistent agent heterogeneity forbids seven-state Markov projection' unless biases.size==6 && biases.uniq.size==1
    (0..6).map do |n|
      dist=S.occupancy_distribution((1<<n)-1,clock:clock,signal:signal,
        strength:strength,tremble:tremble,biases:biases,shock_amplitude:shock_amplitude)
      raise 'invalid kernel' unless (dist.sum-1).abs<1e-10
      dist
    end
  end
  def evaluate(clock:,signal:,strength:,initial:4,horizon:40,**options)
    raise ArgumentError,'invalid initial/horizon' unless (0..6).cover?(initial) && horizon.is_a?(Integer) && horizon.positive?
    k=kernel(clock:clock,signal:signal,strength:strength,**options)
    dist=Array.new(7,0.0);dist[initial]=1.0
    total=0.0
    horizon.times do
      total+=S.expected_excess(dist)
      dist=(0..6).map{|j|(0..6).sum{|i|dist[i]*k[i][j]}}
      raise 'probability lost' unless (dist.sum-1).abs<1e-9
    end
    {cumulative_excess:total,terminal:dist}
  end
  def contrast(strength:,initial:4,**options)
    frozen=evaluate(clock: :simultaneous,signal: :frozen,strength:strength,initial:initial,**options)
    refreshed=evaluate(clock: :sequential,signal: :refreshed,strength:strength,initial:initial,**options)
    {initial:initial,strength:strength,baseline:frozen[:cumulative_excess],
     refreshed:refreshed[:cumulative_excess],interaction:refreshed[:cumulative_excess]-frozen[:cumulative_excess]}
  end
end
