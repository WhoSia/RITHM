# frozen_string_literal: true
require 'json'
# Synthetic 3-agent, two-link atomic congestion game. Individual private
# latency = concurrent occupancy. A unilateral move is evaluated after entry.
module RithmEffortDynamics
  module_function
  def cost(v)
    raise ArgumentError unless v.size==3 && v.all?{|x|[0,1].include?(x)}
    n=v.count(0);n*n+(3-n)*(3-n)
  end
  def change?(v,i,friction)
    own=v.count(v[i]); target=3-own
    own-(target+1)>friction
  end
  def advance(v,friction:0,schedule: :parallel)
    raise ArgumentError unless friction.is_a?(Integer)&&friction>=0
    raise ArgumentError unless [:parallel,:sequential].include?(schedule)
    if schedule==:parallel
      v.each_index.map{|i|change?(v,i,friction) ? 1-v[i] : v[i]}
    else
      w=v.dup
      w.each_index{|i|w[i]=1-w[i] if change?(w,i,friction)}
      w
    end
  end
  def trajectory(initial,horizon:,friction:0,schedule: :parallel)
    raise ArgumentError unless (1..20).cover?(horizon)
    states=[initial]
    horizon.times{states << advance(states.last,friction:friction,schedule:schedule)}
    states
  end
  def verdict(horizon:4,friction:0,schedule: :parallel)
    truth=[0,0,1];a=[0,0,0];b=[1,0,0]
    histories=[truth,a,b].map{|v|trajectory(v,horizon:horizon,friction:friction,schedule:schedule)}
    errors=histories[1..2].map{|path| path.zip(histories[0]).sum{|x,y|(cost(x)-cost(y)).abs}}
    {'assumptions'=>'synthetic simultaneous myopic better-response with linear atomic congestion and threshold friction',
     'horizon'=>horizon,'friction'=>friction,'schedule'=>schedule.to_s,
     'initial_truth'=>truth,'initial_individual_better'=>a,'initial_individual_worse'=>b,
     'initial_hamming_better'=>1,'initial_hamming_worse'=>2,
     'trajectories'=>histories,'cumulative_cost_errors'=>errors,
     'ranking_reversal'=>errors[0]>errors[1],'human_or_causal_claim'=>false}
  end
end
if __FILE__==$PROGRAM_NAME
 puts JSON.pretty_generate(RithmEffortDynamics.verdict(horizon:Integer(ARGV.fetch(0,'4')),friction:Integer(ARGV.fetch(1,'0')),schedule:ARGV.fetch(2,'parallel').to_sym))
end
