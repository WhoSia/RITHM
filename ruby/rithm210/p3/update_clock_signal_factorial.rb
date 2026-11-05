# frozen_string_literal: true
# RITHM P3-R17A: exact six-labelled-player clock x signal-age factorial.
# Six adjustment opportunities in EVERY protocol; no human causal claim.
module Rithm210UpdateClockSignalFactorial
  module_function
  N=6
  ALL=(1<<N)-1
  LOW=Rational(1,10)
  def occupancy(mask)
    raise ArgumentError,'mask' unless mask.is_a?(Integer) && mask.between?(0,ALL)
    mask.to_s(2).count('1')
  end
  def improvement_for_switch(route_a,perceived_n)
    raise ArgumentError,'perceived occupancy' unless perceived_n.is_a?(Integer) && perceived_n.between?(0,N)
    route_a ? 3*perceived_n-14 : 11-3*perceived_n
  end
  def move_probability(route_a,perceived_n,tremble:LOW)
    raise ArgumentError,'tremble must be rational between 0 and 1/2' unless tremble.is_a?(Rational) && tremble>=0 && tremble<=Rational(1,2)
    improvement_for_switch(route_a,perceived_n)>0 ? 1-tremble : tremble
  end
  def switch_distribution(mask,clock:,signal:,observed_n:nil,tremble:LOW)
    raise ArgumentError,'clock/signal' unless %i[simultaneous sequential].include?(clock) && %i[frozen refreshed].include?(signal)
    occupancy(mask)
    old_n=observed_n.nil? ? occupancy(mask) : observed_n
    raise ArgumentError,'old observation' unless old_n.is_a?(Integer) && old_n.between?(0,N)
    if clock==:simultaneous
      public_n=signal==:frozen ? old_n : occupancy(mask)
      states={mask=>1.to_r}
      N.times do |i|
        nxt=Hash.new(0.to_r)
        states.each do |state,mass|
          route=(mask & (1<<i))!=0
          p=move_probability(route,public_n,tremble:tremble)
          nxt[state]+=mass*(1-p)
          nxt[state^(1<<i)]+=mass*p
        end
        states=nxt
      end
      return states
    end
    # DP over [already-selected actor IDs, current labelled route state].
    # Each individual is selected exactly once in a uniformly random order.
    states={[0,mask]=>1.to_r}
    N.times do |step|
      next_states=Hash.new(0.to_r)
      remaining=N-step
      states.each do |(selected,current),weight|
        N.times do |actor|
          bit=1<<actor
          next if (selected & bit)!=0
          route=(current & bit)!=0
          signal_n=signal==:refreshed ? occupancy(current) : old_n
          p=move_probability(route,signal_n,tremble:tremble)
          factor=weight/remaining
          next_states[[selected|bit,current]]+=factor*(1-p)
          next_states[[selected|bit,current^bit]]+=factor*p
        end
      end
      states=next_states
    end
    out=Hash.new(0.to_r)
    states.each do |(selected,current),weight|
      raise 'incomplete actor coverage' unless selected==ALL
      out[current]+=weight
    end
    out
  end
  def summarize(states)
    raise 'probabilities not normalized' unless states.values.sum==1
    hist=Array.new(N+1,0.to_r)
    states.each{|mask,p|hist[occupancy(mask)]+=p}
    mean=hist.each_with_index.sum{|p,n|p*n}
    var=hist.each_with_index.sum{|p,n|p*(n-mean)**2}
    excess=hist.each_with_index.sum{|p,n|p*3*(n-4)**2}
    raise 'quadratic welfare identity' unless excess==3*(var+(mean-4)**2)
    {mean:mean,variance:var,expected_excess:excess,distribution:hist}
  end
  def factorial(initial_mask:15,observed_n:nil,tremble:LOW)
    results={}
    %i[simultaneous sequential].each do |clock|
      %i[frozen refreshed].each do |signal|
        results[[clock,signal]]=summarize(switch_distribution(initial_mask,clock:clock,
          signal:signal,observed_n:observed_n,tremble:tremble))
      end
    end
    cost=->(c,s){results.fetch([c,s])[:expected_excess]}
    interaction=(cost.call(:sequential,:refreshed)-cost.call(:sequential,:frozen))-
      (cost.call(:simultaneous,:refreshed)-cost.call(:simultaneous,:frozen))
    {protocols:results,difference_in_differences:interaction,
      caveat:'Exact synthetic factorial potential outcome under stipulated response, NOT identified human causal effect'}
  end
end
if __FILE__==$PROGRAM_NAME
  require 'json'
  x=Rithm210UpdateClockSignalFactorial.factorial
  puts JSON.pretty_generate({protocols:x[:protocols].to_h{|(c,s),v|
    ["#{c}_#{s}",v.transform_values{|z|z.is_a?(Array) ? z.map(&:to_f) : z.to_f}]},
    difference_in_differences:x[:difference_in_differences].to_f})
end
