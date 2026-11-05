# frozen_string_literal: true
# RITHM P3-R17B: exact-enumerated equal-opportunity 7-state kernel then
# fully autonomous, 40-round occupancy/welfare propagation. No original CSV.
require_relative 'update_clock_signal_factorial'
module Rithm210UpdateClockWelfareRollout
  module_function
  E=Rithm210UpdateClockSignalFactorial
  def kernel(clock:,signal:,tremble:E::LOW)
    (0..6).map do |n|
      mask=(1<<n)-1
      states=E.switch_distribution(mask,clock:clock,signal:signal,observed_n:n,tremble:tremble)
      row=E.summarize(states)[:distribution].map(&:to_f)
      raise 'kernel mass lost' unless (row.sum-1).abs<1e-12
      row
    end
  end
  def evaluate(clock:,signal:,initial:4,horizon:40,tremble:E::LOW)
    raise ArgumentError,'initial and horizon' unless (0..6).cover?(initial) && horizon.is_a?(Integer) && horizon.positive?
    transition=kernel(clock:clock,signal:signal,tremble:tremble)
    dist=Array.new(7,0.0);dist[initial]=1.0
    loss=0.0;path=[]
    horizon.times do |t|
      current=(0..6).sum{|n|dist[n]*3*(n-4)**2}
      loss+=current
      path<<{period:t+1,expected_excess:current,mean_n:(0..6).sum{|n|dist[n]*n}}
      dist=(0..6).map{|j|(0..6).sum{|i|dist[i]*transition[i][j]}}
      raise 'distribution mass lost' unless (dist.sum-1).abs<1e-10
    end
    {clock:clock,signal:signal,initial:initial,horizon:horizon,
      cumulative_excess:loss,terminal_distribution:dist,path:path,
      opportunities_per_round:6}
  end
  def factorial(initial:4,horizon:40)
    protocols={}
    %i[simultaneous sequential].each do |clock|
      %i[frozen refreshed].each do |signal|
        protocols[[clock,signal]]=evaluate(clock:clock,signal:signal,
          initial:initial,horizon:horizon)
      end
    end
    f=->(c,s){protocols.fetch([c,s])[:cumulative_excess]}
    interaction=(f.call(:sequential,:refreshed)-f.call(:sequential,:frozen))-
      (f.call(:simultaneous,:refreshed)-f.call(:simultaneous,:frozen))
    {protocols:protocols,interaction:interaction}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  x=Rithm210UpdateClockWelfareRollout.factorial
  puts JSON.pretty_generate({protocols:x[:protocols].to_h{|(c,s),v|
    ["#{c}_#{s}",{cumulative_excess:v[:cumulative_excess],
     final_mean:v[:path].last[:mean_n],final_expected_excess:v[:path].last[:expected_excess]}]},
     interaction:x[:interaction]})
end
