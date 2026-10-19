# frozen_string_literal: true
require_relative '../p0/paid_agency'
# Backward equilibrium court for TWO strategic agents with PUBLIC last actions.
# Each round privately computed parity is a fresh iid two-bit world, but
# realized actions become public before the next round. Every actor chooses
# STOP (route 0) or COMPUTE (READ X, READ Y, XOR, ACT parity) before the shock.
# Contractual two-program action set. No learning, no claim of unique SPE.
module Rithm29DynamicCourt
 module_function
 def run(horizon:3,read_fee:Rational(1,4),xor_fee:Rational(1,2),
         wrong:2,switch_fee:Rational(1,2))
  raise ArgumentError unless (1..6).cover?(horizon) && [read_fee,xor_fee,wrong,switch_fee].all?{|x|x>=0}
  v=Array.new(horizon+1){{}}
  [0,1].product([0,1]).each{|prev|v[0][prev]=[0,0]}
  policies={}
  1.upto(horizon) do |t|
   [0,1].product([0,1]).each do |prev|
    rows=Rithm29PaidAgency::POLICIES.product(Rithm29PaidAgency::POLICIES).map do |pair|
     losses=[0,0];social=0
     Rithm29PaidAgency::WORLDS.each do |world|
      out=Rithm29PaidAgency.outcome(pair,world,read_fee:read_fee,xor_fee:xor_fee,mismatch_loss:wrong)
      after=out[:routes]
      2.times{|i|losses[i]+=Rational(out[:individual][i]+(after[i]!=prev[i] ? switch_fee : 0)+v[t-1][after][i],4)}
     end
     {programs:pair,costs:losses}
    end
    equil=rows.select do |row|
     2.times.all? do |i|
      rows.select{|o|o[:programs][1-i]==row[:programs][1-i]}.all?{|o|o[:costs][i]>=row[:costs][i]}
     end
    end
    # NOT a unique equilibrium theorem. Halt rather than silently substitute an optimum.
    raise "no pure subgame Nash at t=#{t}, prev=#{prev.inspect}" if equil.empty?
    # Fully disclosed deterministic equilibrium selector: lowest social sum,
    # then lexical STOP before COMPUTE. Selection is not behavioral evidence.
    pick=equil.min_by{|e|[e[:costs].sum,e[:programs].map{|p|p==:stop ? 0 : 1}]}
    v[t][prev]=pick[:costs]
    policies[[t,prev]]= {selected:pick,equilibrium_count:equil.size,
      all_equilibria:equil}
   end
  end
  {horizon:horizon,initial_prev:[0,0],expected_costs:v[horizon][[0,0]],
   expected_social:v[horizon][[0,0]].sum,policies:policies,
   equilibrium_contract:'pure behavioral Markov equilibrium under public joint last-action and shared fresh parity',
   limited_action_space:true,unique_equilibrium_certified:false,
   no_human_causal_claim:true}
 end
end
