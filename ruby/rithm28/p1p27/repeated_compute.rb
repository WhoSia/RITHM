# frozen_string_literal: true
require_relative '../p1p25/finite_procedure'
# An explicitly contracted bridge: each round a controller must predict XOR
# of two fresh independent hidden bits, then route an action whose mismatch
# produces L congestion surcharge. No game-theoretic equilibrium assertion.
module RithmRepeatedCompute
 module_function
 def compare(rounds:,read_fee:,xor_fee:,wrong_loss:4,reset_cost:0)
   raise ArgumentError unless rounds.is_a?(Integer) && rounds.between?(1,100) && reset_cost>=0
   one=RithmFiniteProcedure.solve(read_fee:read_fee,xor_fee:xor_fee,wrong_loss:wrong_loss)
   compute=one.fetch('two_reads_and_compute_cost')
   stop=one.fetch('stop_expected_cost')
   # State refresh makes past observed bits uninformative about next round.
   # Reset charges on rounds 2..T only if full procedure is run each round.
   full_total=rounds*compute+(rounds-1)*reset_cost
   stop_total=rounds*stop
   break_even=full_total<stop_total
   {'rounds'=>rounds,'compute_all_expected_cost'=>full_total,
    'never_compute_expected_cost'=>stop_total,'compute_all_better'=>break_even,
    'cost_comparison_only'=>true,'real_route_behavior_identified'=>false,
    'mixed_strategy_equilibrium'=>false,
    'qualification'=>'independent fresh worlds; restricted paid ISA, no strategic opponents'}
 end
end
