# frozen_string_literal: true
# One-agent finite-horizon Bellman court. Parity is a new fair bit each round.
# Opponent action is fixed at 0; congestion adds 1 if own action 1, 2 if 0.
# Agent knows previous action and can: STOP (choose previous route or 0/1)
# without state observation, or PAY then observe parity and choose 0/1.
# This is a complete one-agent best response, NOT a multi-agent MPE.
module Rithm29Bellman
 module_function
 def immediate(action,prev,parity,observed,fee,k,wrong)
   (action==0 ? 2 : 1) + (action==parity ? 0 : wrong) +
     (action==prev ? 0 : k) + (observed ? fee : 0)
 end
 def solve(horizon:,fee:Rational(1),k:Rational(1,2),wrong:2,opponent:0)
   raise ArgumentError unless horizon.between?(1,12)&&fee>=0&&k>=0&&wrong>=0&&opponent==0
   v=Array.new(horizon+1){Array.new(2,0)};pol={}
   1.upto(horizon) do |t|
     2.times do |prev|
       no=[0,1].map{|a| [a,(0..1).sum{|z|Rational(immediate(a,prev,z,false,fee,k,wrong),2)}+v[t-1][a]]}
       inspect=Rational(fee)
       branches={}
       2.times do |z|
         branch=[0,1].map{|a|[a,immediate(a,prev,z,false,fee,k,wrong)+v[t-1][a]]}.min_by{|a,c|[c,a]}
         branches[z]=branch[0]
         inspect+=Rational(branch[1],2)
       end
       keep=no.min_by{|a,c|[c,a]}
       if inspect<keep[1]
         v[t][prev]=inspect;pol[[t,prev]]={instruction: :inspect,actions: branches}
       else
         v[t][prev]=keep[1];pol[[t,prev]]={instruction: :stop,action:keep[0]}
       end
     end
   end
   {value:v[horizon][0],values:v,policy:pol,horizon:horizon,initial_action:0,
    other_agent_fixed:true,strategic_game_equilibrium:false}
 end
end
