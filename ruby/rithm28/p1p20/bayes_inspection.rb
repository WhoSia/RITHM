# frozen_string_literal: true
require 'json'
# A true finite hidden-payoff observation model: before inspection the agent
# does NOT know which binary world obtains; inspection reveals it for q.
# Monetary regret: wrong action L; switching current action 0 -> 1 costs k.
module RithmBayesInspection
  module_function
  def judge(prior_numerator:,loss:,switch_cost:,inspection_cost:)
    p=prior_numerator; l=loss; k=switch_cost; q=inspection_cost
    raise ArgumentError,'integer input range' unless [p,l,k,q].all?{|v|v.is_a?(Integer)} && p.between?(0,4) && l>0 && k>=0 && q>=0
    # All numerators are on a denominator-4 grid; no floating arithmetic.
    stay= p*l
    switch= (4-p)*l+4*k
    without=[stay,switch].min
    # After perfect inspection, in world 1 switching avoids loss iff k<l;
    # world 0 staying is always optimal.
    with= p*[k,l].min+4*q
    stop_action=stay<=switch ? 0 : 1
    use_inspection=with<without # ties avoid unnecessary computation
    { 'prior_probability_world_one'=>"#{p}/4",'loss'=>l,'switch_cost'=>k,
      'inspection_cost'=>q,'stop_policy_action'=>stop_action,
      'stop_expected_cost_numerator'=>without,
      'inspect_expected_cost_numerator'=>with,
      'decision'=>use_inspection ? 'inspect' : 'stop',
      'inspection_value_numerator'=>without-p*[k,l].min,
      'net_gain_numerator'=>without-with,
      'world_observed_before_decision'=>false,
      'empirical_identification'=>false }
  end
end
if __FILE__==$PROGRAM_NAME
  puts JSON.pretty_generate(RithmBayesInspection.judge(prior_numerator:Integer(ARGV.fetch(0,'2')),
    loss:Integer(ARGV.fetch(1,'4')),switch_cost:Integer(ARGV.fetch(2,'0')),inspection_cost:Integer(ARGV.fetch(3,'1'))))
end
