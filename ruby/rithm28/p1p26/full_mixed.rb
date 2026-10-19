# frozen_string_literal: true
require_relative '../p1p23/three_agent'
module RithmFullMixedCourt
 module_function
 G=RithmThreeAgentInspection
 STAY=[false,0,0].freeze
 ACQUIRE=[true,0,1].freeze
 B_STAY=[false,1,1].freeze
 def expectation_of_deviation(i,alternative,x,k:,q:,p:)
   weights=[[STAY,1-x],[ACQUIRE,x]]
   total=0
   weights.product(weights).each do |left,right|
     ps=[left[0],right[0],B_STAY]
     ps[i]=alternative
     total+=left[1]*right[1]*G.expected(ps,k:k,q:q,p:p)[0][i]
   end
   total
 end
 def certificate(q:,k:Rational(3,4),p:Rational(1,2))
   raise ArgumentError,'fixed parameters' unless k==Rational(3,4)&&p==Rational(1,2)
   raise ArgumentError,'outside support' unless q>=0 && q<=Rational(1,8)
   x=Rational(1,8)-q
   costs=3.times.map do |i|
     G::PLANS.map{|a|expectation_of_deviation(i,a,x,k:k,q:q,p:p)}
   end
   supported=[0,1].all?{|i| costs[i][0]==costs[i][G::PLANS.index(ACQUIRE)] && costs[i].all?{|v|v>=costs[i][0]}}
   third=costs[2].all?{|v|v>=costs[2][1]}
   raise 'full-game deviation failed' unless supported && third
   welfare=0
   [[STAY,1-x],[ACQUIRE,x]].product([[STAY,1-x],[ACQUIRE,x]]).each do |left,right|
     welfare+=left[1]*right[1]*G.expected([left[0],right[0],B_STAY],k:k,q:q,p:p)[1]
   end
   {'q'=>q,'x'=>x,'expected_individual_losses'=>costs,
    'expected_social_cost'=>welfare,'full_game_deviations_verified'=>true,
    'equilibrium_type'=>'full-three-agent independent mixed Nash on explicit restricted support',
    'claim_scope'=>'one family, not all mixed equilibria'}
 end
end
