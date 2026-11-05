# frozen_string_literal: true
# R17E: 64-state labelled welfare dynamics required for persistent actor heterogeneity.
require_relative 'smooth_clock_welfare_rollout'
module Rithm210LabeledSmoothWelfareRollout
  module_function
  S=Rithm210SmoothSignalClock
  Base=Rithm210UpdateClockSignalFactorial
  def kernel(clock:,signal:,strength:,tremble:0.1,biases:Array.new(6,0.0),shock_amplitude:0.0)
    (0..63).map do |mask|
      states=S.transition(mask,clock:clock,signal:signal,strength:strength,tremble:tremble,
        biases:biases,shock_amplitude:shock_amplitude)
      row=Array.new(64,0.0)
      states.each{|to,p|row[to]+=p}
      raise 'invalid transition' unless (row.sum-1).abs<1e-9
      row
    end
  end
  def evaluate(clock:,signal:,strength:,initial_mask:15,horizon:40,**params)
    Base.occupancy(initial_mask)
    raise ArgumentError,'positive integer horizon required' unless horizon.is_a?(Integer) && horizon.positive?
    k=kernel(clock:clock,signal:signal,strength:strength,**params)
    dist=Array.new(64,0.0);dist[initial_mask]=1.0
    total=0.0
    horizon.times do
      total+=(0..63).sum{|mask|dist[mask]*3*(Base.occupancy(mask)-4)**2}
      next_dist=Array.new(64,0.0)
      dist.each_with_index do |mass,mask|
        next if mass.zero?
        k[mask].each_with_index{|p,to|next_dist[to]+=mass*p}
      end
      raise 'probability lost' unless (next_dist.sum-1).abs<1e-9
      dist=next_dist
    end
    terminal=(0..6).map{|n|(0..63).sum{|mask|Base.occupancy(mask)==n ? dist[mask] : 0.0}}
    {cumulative_excess:total,terminal_occupancy:terminal,terminal_microstate:dist}
  end
end
