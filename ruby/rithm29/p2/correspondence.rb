# frozen_string_literal: true
require 'json'
# Full pure Markov equilibrium correspondence under a contracted three-program ISA.
# Every public previous joint action gets its own pure equilibrium continuation.
module Rithm29Correspondence
 module_function
 PROGRAMS=[:stop0,:stop1,:compute].freeze
 STATES=[0,1].product([0,1]).freeze
 WORLDS=STATES
 def outcome(pair,prev,world,fee:,switch:,wrong:)
  z=world[0]^world[1]
  actions=pair.map{|p|p==:stop0 ? 0 : p==:stop1 ? 1 : z}
  costs=2.times.map{|i|actions.count(actions[i])+(actions[i]==z ? 0 : wrong)+(pair[i]==:compute ? fee : 0)+(actions[i]==prev[i] ? 0 : switch)}
  [actions,costs]
 end
 def state_equilibria(future,prev,fee:,switch:,wrong:)
  rows=PROGRAMS.product(PROGRAMS).map do |pair|
   costs=[0,0]
   WORLDS.each do |w|
    a,c=outcome(pair,prev,w,fee:fee,switch:switch,wrong:wrong)
    2.times{|i|costs[i]+=Rational(c[i]+future.fetch(a)[i],4)}
   end
   [pair,costs]
  end
  rows.select{|pair,costs|2.times.all?{|i|
    rows.all?{|alt,other|alt[1-i]!=pair[1-i] || other[i]>=costs[i]}
  }}
 end
 def enumerate(horizon:,fee:1,switch:Rational(1,2),wrong:2,limit:100_000)
  raise ArgumentError unless horizon.between?(1,4)&&[fee,switch,wrong].all?{|x|x>=0}
  branches=[[STATES.to_h{|s|[s,[0,0]]},[]]]
  levels=[]
  1.upto(horizon) do |t|
   upcoming=[]
   branches.each do |continuation,hist|
    sets=STATES.map{|s|state_equilibria(continuation,s,fee:fee,switch:switch,wrong:wrong)}
    next if sets.any?(&:empty?)
    possible=sets.map(&:length).inject(1,:*)
    return {complete:false,period:t,lower_bound:upcoming.length+possible,previous_count:branches.length} if upcoming.length+possible>limit
    sets[0].product(*sets[1..]).each do |choices|
      nxt=STATES.each_with_index.to_h{|s,i|[s,choices[i][1]]}
      upcoming<<[nxt,hist+[choices.map(&:first)]]
    end
   end
   branches=upcoming;levels<<branches.length
  end
  welfare=branches.map{|continuation,_|continuation.fetch([0,0]).sum}.uniq.sort
  {complete:true,horizon:horizon,branch_counts:levels,equilibrium_policies:branches.size,
    welfare_values:welfare,minimum:welfare.min,maximum:welfare.max,
    qualification:'all pure Markov policy continuations in specified three-program finite game only'}
 end
end
if $PROGRAM_NAME==__FILE__
 r=Rithm29Correspondence.enumerate(horizon:3)
 puts JSON.pretty_generate(r.transform_values{|v|v.is_a?(Rational) ? v.to_s : v})
end
