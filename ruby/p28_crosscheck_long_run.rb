#!/usr/bin/env ruby
# Independently check exact P28 Go vs C++ per-policy integer output; export ONLY aggregate panel bounds.
require 'csv';require 'json'
raise 'usage: ruby crosscheck_long_run.rb go.json cpp.csv panel_bounds.csv' unless ARGV.length==3
gofile,cppfile,out=ARGV
j=JSON.parse(File.read(gofile));rows=CSV.read(cppfile,headers:true)
raise 'only 18 policy-budget rows' unless rows.size==18
raise 'source independent 2017 six sessions' unless j.fetch('n_sessions')==6&&j.fetch('n_treatment_panels')==24&&j.fetch('n_group_rounds')==480
checks=0
rows.each do |r|
  name=r.fetch('policy');budget=r.fetch('B');node=j.fetch('result').fetch(name)
  entry=node.fetch('panels_budget_B').fetch(budget)
  raise "C++ vs Go disagreement at #{name}/#{budget}" unless r['lower_total'].to_i==entry.fetch('lower_total')&&r['upper_total'].to_i==entry.fetch('upper_total')
  rect=node.fetch('source_rectangular')
  raise "P27 unrestricted source-rectangular disagreement" unless r['independent_lower'].to_i==rect.fetch('lower_total') && r['independent_upper'].to_i==rect.fetch('upper_total')
  raise 'source opportunities mismatch' unless r['eligible_events'].to_i==node.fetch('opportunity_events')
  raise 'bounds inversion' unless entry['lower_total']<=0 && 0<=entry['upper_total']
  checks+=1
end
panel_lines=[]
j.fetch('panels').each do |p|
 p.fetch('budgets').each do |budget,value|
  panel_lines<<[p.fetch('session'),p.fetch('group'),p.fetch('stage'),p.fetch('info'),p.fetch('policy'),budget.to_i,value.fetch('Lower'),value.fetch('Upper')]
 end
end
raise 'expect 24 panels × 3 policies × 6 budgets' unless panel_lines.size==432
CSV.open(out,'w') do |f|
 f<<%w[session group stage info policy lifetime_budget_B lower_total upper_total]
 panel_lines.each{|x|f<<x}
end
puts "P28_PASS: #{checks}/18 Go-vs-C++ exact long-run cases and 432 non-person-level panel budget rows; no causal effect inferred"
