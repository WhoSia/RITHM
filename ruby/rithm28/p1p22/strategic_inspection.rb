# frozen_string_literal: true
require 'json'
# Exact pure Bayes-Nash normal-form game: two initially-A agents choose
# whether to inspect binary shock, and condition their route on it.
# Third initially-B agent is fixed by contract. Every payoff anticipates
# the other player's entire contingent plan; no level-0 assumption.
module RithmStrategicInspection
  module_function
  PLANS = [[false,0,0],[false,1,1]] + [0,1].product([0,1]).map{|a,b|[true,a,b]}
  def outcome(plans,z,k,q)
    routes=[plans[0][z+1],plans[1][z+1],1]
    na=routes.count(0); nb=3-na
    individual=2.times.map do |i|
      (routes[i]==0 ? na+z : nb) + (routes[i]==1 ? k : 0) + (plans[i][0] ? q : 0)
    end
    {'routes'=>routes,'individual'=>individual,'total'=>
      na*(na+z)+nb*nb+routes.first(2).count(1)*k+plans.count{|p|p[0]}*q}
  end
  def expected(plans,k:,q:,p:)
    a=outcome(plans,0,k,q);b=outcome(plans,1,k,q)
    {'individual'=>2.times.map{|i|(1-p)*a['individual'][i]+p*b['individual'][i]},
     'social'=>(1-p)*a['total']+p*b['total']}
  end
  def equilibria(k:Rational(3,4),q:Rational(1,16),p:Rational(1,2))
    raise ArgumentError unless k>=0 && q>=0 && p.between?(0,1)
    equilibria=[]
    PLANS.product(PLANS).each do |plans|
      current=expected(plans,k:k,q:q,p:p)
      stable=2.times.all? do |i|
        PLANS.all? do |alternative|
          other=plans.dup;other[i]=alternative
          expected(other,k:k,q:q,p:p)['individual'][i]>=current['individual'][i]
        end
      end
      equilibria<<{'plans'=>plans,'individual_cost'=>current['individual'],
        'social_cost'=>current['social']} if stable
    end
    {'k'=>k,'q'=>q,'p'=>p,'pure_equilibria'=>equilibria,
      'all_pure_contingent_profiles_checked'=>PLANS.size**2,
      'third_agent_fixed'=>true,'mixed_equilibria_examined'=>false,
      'source'=>'constructed game only'}
  end
end
if __FILE__==$PROGRAM_NAME
 a=RithmStrategicInspection.equilibria
 puts JSON.pretty_generate(a.transform_values{|v|v.is_a?(Rational) ? v.to_s : v})
end
