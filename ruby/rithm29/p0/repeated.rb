# frozen_string_literal: true
require_relative 'paid_agency'
module Rithm29Repeated
 module_function
 # For every world-path, each player uses an invariant finite program STOP or COMPUTE.
 # The last action persists across rounds for the physical switching fee k.
 def evaluate(programs:,horizon:,switch_fee:,read_fee:Rational(1,4),xor_fee:Rational(1,2),mismatch_loss:2)
  raise ArgumentError unless (1..6).cover?(horizon)&&switch_fee>=0
  raise ArgumentError unless programs.length==2 && programs.all?{|p|Rithm29PaidAgency::POLICIES.include?(p)}
  trajectories=Rithm29PaidAgency::WORLDS.repeated_permutation(horizon)
  sum=0; count=0
  trajectories.each do |seq|
   prev=[0,0]; total=0
   seq.each do |world|
    out=Rithm29PaidAgency.outcome(programs,world,read_fee:read_fee,xor_fee:xor_fee,mismatch_loss:mismatch_loss)
    routes=out.fetch(:routes)
    moves=2.times.count{|i|routes[i]!=prev[i]}
    total+=out.fetch(:social)+moves*switch_fee
    prev=routes
   end
   sum+=total;count+=1
  end
  {programs:programs,horizon:horizon,expected_total:sum/count,
   trajectories:count, prior_route:[0,0],switch_fee:switch_fee,
   policy_scope:'fixed per-agent instruction program each round, not best responses',
   long_run_equilibrium_verified:false}
 end
 def comparison(horizon:3,switch_fee:Rational(1,2))
  ps=Rithm29PaidAgency::POLICIES.product(Rithm29PaidAgency::POLICIES)
  ps.map{|pair|evaluate(programs:pair,horizon:horizon,switch_fee:switch_fee)}
 end
end
