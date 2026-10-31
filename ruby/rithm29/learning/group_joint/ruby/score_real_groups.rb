# frozen_string_literal: true
require 'csv'
require_relative 'group_scoring'
actor_last={}
groups=Hash.new { |h,k| h[k]=[] }
input,output=ARGV
abort 'usage: ruby score_real_groups.rb one_step_predictions.csv output.csv' unless input && output
CSV.foreach(input,headers:true) do |r|
  who=%w[trt session section Group ID].map { |k| r.fetch(k).to_i }
  t=Integer(r.fetch('Period'))
  route=Integer(r.fetch('RouteA'))
  raise 'invalid route' unless [0,1].include?(route)
  prior=actor_last[who]
  raise 'missing or noncontiguous history' if (t==1 && prior) || (t>1 && (!prior || prior[:t]!=t-1))
  if t>1
    key=%w[trt session section Group Period].map { |k| r.fetch(k).to_i }
    groups[key] << [prior[:route],route,Float(r.fetch('p_ewa'))]
  end
  actor_last[who]={t:t,route:route}
end
raise "expected 5616 groups got #{groups.length}" unless groups.length==5616
CSV.open(output,'w') do |csv|
  csv << %w[trt session section Group Period n_prev n_actual U D p_ud joint_logloss count_logloss count_brier expected_cost realized_cost expected_switch actual_switch p_cancel cancel]
  groups.sort.each do |key,people|
    raise 'not six actors' unless people.length==6
    prev=people.map(&:first); actual=people.map { |p| p[1] }; forecasts=people.map(&:last)
    s=RithmGroupScoring.evaluate(previous:prev,probability_a:forecasts,observed_a:actual)
    u=people.count { |p| p[0]==0 && p[1]==1 };d=people.count { |p| p[0]==1 && p[1]==0 }
    csv << [*key,prev.sum,actual.sum,u,d,Math.exp(-s[:joint_logloss]),s[:joint_logloss],s[:count_logloss],s[:count_brier],s[:expected_cost],s[:realized_cost],s[:forecast_switchers],s[:actual_switchers],s[:cancellation_probability],s[:actual_cancellation]]
  end
end
warn "scored #{groups.size} group periods"
