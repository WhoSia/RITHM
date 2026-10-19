# frozen_string_literal: true
require_relative '../p1p23/three_agent'
require 'json'
# Exact rational cross-section: pure Nash equilibria of FULL strategic
# contingent-plan game across information-price grid. No equilibrium selection.
module RithmPriceFrontier
  module_function
  def scan
    q_values=(0..16).map{|j|Rational(j,16)}
    results=q_values.map do |q|
      r=RithmThreeAgentInspection.audit(k:Rational(3,4),q:q,p:Rational(1,2))
      eq=r.fetch('pure_equilibria')
      costs=eq.map{|x|x.fetch('social')}
      {'q'=>q.to_s,'pure_count'=>eq.size,
       'best_cost'=>costs.min&.to_s,'worst_cost'=>costs.max&.to_s,
       'has_welfare_inferior_pure'=>costs.any?{|c|c>6},
       'full_profiles'=>r.fetch('profiles')}
    end
    {'schema'=>'rithm.p1p24.costly_information_price_frontier.v1',
     'baseline_cost'=>'6/1','grid'=>results,
     'scope'=>'pure equilibria only, three agents, all six contingent plans',
     'no_mixed_or_stability_claim'=>true}
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(RithmPriceFrontier.scan)
end
