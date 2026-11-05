# frozen_string_literal: true
# RITHM R17E: smooth heterogeneous actor response with optional binary common shock.
# Entirely synthetic. Six chances per round, frozen versus updated disclosure.
require_relative 'update_clock_signal_factorial'
module Rithm210SmoothSignalClock
  module_function
  Base=Rithm210UpdateClockSignalFactorial
  N=6
  ALL=(1<<N)-1
  def sigmoid(x)
    x>=0 ? 1.0/(1.0+Math.exp(-x)) : (v=Math.exp(x);v/(1.0+v))
  end
  def validate!(strength:,tremble:,biases:,shock:)
    raise ArgumentError,'finite nonnegative strength' unless strength.is_a?(Numeric) && strength.finite? && strength>=0
    raise ArgumentError,'tremble in [0,0.5]' unless tremble.is_a?(Numeric) && tremble.finite? && tremble.between?(0,0.5)
    raise ArgumentError,'six finite individual biases' unless biases.is_a?(Array) && biases.size==N && biases.all?{|v|v.is_a?(Numeric) && v.finite?}
    raise ArgumentError,'finite shock' unless shock.is_a?(Numeric) && shock.finite?
  end
  def probability(route_a,perceived_n,actor:,strength:,tremble:,biases:,shock:)
    raise ArgumentError,'actor index' unless actor.between?(0,N-1)
    gain=Base.improvement_for_switch(route_a,perceived_n)
    tremble+(1.0-2.0*tremble)*sigmoid(strength*gain+biases.fetch(actor)+shock)
  end
  def conditional_transition(mask,clock:,signal:,observed_n:nil,strength:1.0,tremble:0.0,biases:Array.new(N,0.0),shock:0.0)
    Base.occupancy(mask)
    validate!(strength:strength,tremble:tremble,biases:biases,shock:shock)
    raise ArgumentError,'clock/signal' unless %i[simultaneous sequential].include?(clock) && %i[frozen refreshed].include?(signal)
    reported=observed_n.nil? ? Base.occupancy(mask) : observed_n
    raise ArgumentError,'observed occupancy' unless reported.is_a?(Integer) && reported.between?(0,N)
    if clock==:simultaneous
      public_n=signal==:frozen ? reported : Base.occupancy(mask)
      states={mask=>1.0}
      N.times do |i|
        nxt=Hash.new(0.0)
        route_a=(mask & (1<<i))!=0
        p=probability(route_a,public_n,actor:i,strength:strength,tremble:tremble,biases:biases,shock:shock)
        states.each{|state,mass|nxt[state]+=mass*(1-p);nxt[state^(1<<i)]+=mass*p}
        states=nxt
      end
      return states
    end
    states={[0,mask]=>1.0}
    N.times do |step|
      nxt=Hash.new(0.0)
      remaining=N-step
      states.each do |(selected,current),weight|
        N.times do |actor|
          bit=1<<actor
          next unless (selected & bit)==0
          route_a=(current & bit)!=0
          signal_n=signal==:refreshed ? Base.occupancy(current) : reported
          p=probability(route_a,signal_n,actor:actor,strength:strength,tremble:tremble,biases:biases,shock:shock)
          share=weight/remaining
          nxt[[selected|bit,current]]+=share*(1-p)
          nxt[[selected|bit,current^bit]]+=share*p
        end
      end
      states=nxt
    end
    out=Hash.new(0.0)
    states.each do |(selected,current),weight|
      raise 'missing actor' unless selected==ALL
      out[current]+=weight
    end
    out
  end
  def transition(mask,clock:,signal:,shock_amplitude:0.0,**options)
    raise ArgumentError,'shock amplitude finite nonnegative' unless shock_amplitude.is_a?(Numeric) && shock_amplitude.finite? && shock_amplitude>=0
    return conditional_transition(mask,clock:clock,signal:signal,shock:0.0,**options) if shock_amplitude==0
    minus=conditional_transition(mask,clock:clock,signal:signal,shock:-shock_amplitude,**options)
    plus=conditional_transition(mask,clock:clock,signal:signal,shock:shock_amplitude,**options)
    result=Hash.new(0.0)
    minus.each{|state,v|result[state]+=0.5*v}
    plus.each{|state,v|result[state]+=0.5*v}
    result
  end
  def occupancy_distribution(mask,**args)
    states=transition(mask,**args)
    out=Array.new(7,0.0)
    states.each{|state,v|out[Base.occupancy(state)]+=v}
    raise 'mass lost' unless (out.sum-1).abs<1e-9
    out
  end
  def expected_excess(dist)
    dist.each_with_index.sum{|p,n|3*(n-4)**2*p}
  end
  def factorial(mask:15,observed_n:nil,**parameters)
    conditions={}
    %i[simultaneous sequential].each do |clock|
      %i[frozen refreshed].each do |signal|
        dist=occupancy_distribution(mask,clock:clock,signal:signal,observed_n:observed_n,**parameters)
        conditions[[clock,signal]]={occupancy_distribution:dist,excess:expected_excess(dist)}
      end
    end
    e=->(c,s){conditions.fetch([c,s])[:excess]}
    {conditions:conditions,interaction:(e.call(:sequential,:refreshed)-e.call(:sequential,:frozen))-
      (e.call(:simultaneous,:refreshed)-e.call(:simultaneous,:frozen))}
  end
  def lumpability_witness(mask_a:,mask_b:,**parameters)
    raise ArgumentError,'require same occupancy' unless Base.occupancy(mask_a)==Base.occupancy(mask_b)
    a=occupancy_distribution(mask_a,clock: :simultaneous,signal: :frozen,**parameters)
    b=occupancy_distribution(mask_b,clock: :simultaneous,signal: :frozen,**parameters)
    {a:a,b:b,total_variation:a.zip(b).sum{|x,y|(x-y).abs}/2.0}
  end
end
