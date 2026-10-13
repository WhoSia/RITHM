#!/usr/bin/env ruby
# Independent Go/C++ agreement gate, matching exactly 9 policy×k scenarios.
require 'csv'
require 'json'
raise 'usage: ruby verify_envelopes.rb go.json cpp.csv' unless ARGV.length==2
a=JSON.parse(File.read(ARGV[0]));b=CSV.read(ARGV[1], headers:true)
raise 'missing scenarios' unless a.size==9 && b.size==9
bykey=a.to_h{|x|[[x.fetch('scheme'),x.fetch('max_switched_eligible_c')],x]}
b.each do |x|
  key=[x['scheme'],Integer(x['k'])]; g=bykey.fetch(key)
  {"N"=>"n_group_rounds", "both"=>"both_signs_feasible", "benefit"=>"benefit_feasible", "harm"=>"harm_feasible"}.each do |a_field,b_field|
    raise "disagreement #{key} #{a_field}" unless Integer(x[a_field])==g[b_field]
  end
  {"mean_lower"=>"mean_sharp_lower_cost_gain", "mean_upper"=>"mean_sharp_upper_cost_gain"}.each do |a_field,b_field|
    raise "numeric disagreement #{key} #{a_field}" unless (Float(x[a_field])-g[b_field]).abs<1e-10
  end
end
original=bykey.fetch(['unrestricted',1]);
raise 'P24 gate failed' unless original['both_signs_feasible']==369 && original['harm_feasible']==472
incident=bykey.fetch(['incident_avoid',1]);
raise 'incident sign invalid' unless incident['mean_sharp_lower_cost_gain']==0 && incident['harm_feasible']==0
puts "RUBY_MULTILANG_GATE PASS 9/9 Go vs C++ policy×budget cells; 480 historical group rounds"
