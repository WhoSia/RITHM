#!/usr/bin/env ruby
# 2017 source-derived de-identified stable-subject-slot history audit, not new advice exposure.
require 'csv'
require 'json'
require 'digest'
abort('usage: ruby audit_human_history.rb compact_routes.csv') unless ARGV.length==1
src=ARGV[0]
rows=CSV.read(src, headers:true)
raise "need 24 panels" unless rows.length==24
n_eligible=0;incidents=0;panel_person=0;people_c2=0;people_c1=0;people_visit=0; total_transitions=0;arr=[]
rows.each do |p|
 number=p.fetch('choices_base3_hex').to_i(16)
 route=Array.new(20){Array.new(12)}
 19.downto(0) do |t|
  11.downto(0) do |i|
   route[t][i]=number%3+1
   number/=3
  end
 end
 raise 'base3 source overflow' unless number.zero?
 bits=p.fetch('incident_20_bits_hex').to_i(16)
 raise 'non 4/20 incident design' unless bits.to_s(2).count('1')==4
 20.times do |t|
  incidents+=(bits>>(19-t))&1
  n_eligible+=route[t].count{|v| v!=1}
 end
 12.times do |i|
  panel_person+=1
  eligible=route.map{|rs| rs[i]}.reject{|v|v==1}
  people_visit+=1 if eligible.any?
  switches=eligible.each_cons(2).count{|a,b|a!=b}
  total_transitions+=switches
  people_c2+=1 if switches>=2
  people_c1+=1 if switches>=1
  arr << switches
 end
end
output={"source_sha256"=>Digest::SHA256.file(src).hexdigest,"source"=>"Wijayaratna 2017 original human route panel compact; no individual identity exported", "panels"=>rows.length,"source_sessions"=>rows.map{|v|v['session']}.uniq.size,"panel_person_slots"=>panel_person,"total_eligible_C_visits"=>n_eligible,"total_incident_group_rounds"=>incidents,"slots_with_any_C_visit"=>people_visit,"slots_with_at_least_1_historical_CB_CD_switch"=>people_c1,"slots_with_at_least_2_historical_CB_CD_switches"=>people_c2,"observed_C_branch_switches_across_successive_eligible_visits"=>total_transitions,"distribution"=>arr.tally.sort.to_h, "WARNING"=>"Observed branch changes between eligible visits are ordinary route-choice dynamics, not additional advice-induced compliance. Per-person one *extra* switch is an unverified counterfactual restriction; history cannot identify response budget."}
puts JSON.pretty_generate(output)
