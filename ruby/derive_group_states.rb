#!/usr/bin/env ruby
# Stage-faithful de-identified aggregate reconstruction from verified 2017 S2 compact routes.
# No original copyrighted XLSX or person-level row redistribution.
require 'csv'
require 'digest'
raise 'usage: ruby derive_group_states.rb compact_routes.csv states.csv' unless ARGV.size == 2
source, output = ARGV
rows=CSV.read(source,headers:true)
raise 'expect 24 panels' unless rows.length==24
states=[]
rows.each do |p|
  number = p.fetch('choices_base3_hex').to_i(16)
  routes=Array.new(240)
  239.downto(0) do |i|
    routes[i]=(number%3)+1
    number/=3
  end
  raise 'noncanonical overflow' unless number==0
  bits=p.fetch('incident_20_bits_hex').to_i(16)
  raise 'invalid incident count' unless bits.to_s(2).count('1')==4
  20.times do |j|
    block=routes.slice(j*12,12)
    n1,n2,n3=(1..3).map{|v|block.count(v)}
    z=(bits>>(19-j))&1
    cost=264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2
    states<<[p.fetch('session'),p.fetch('group'),p.fetch('stage'),p.fetch('info'),j+1,n1,n2,n3,z,cost]
  end
end
raise 'expected 480 group-rounds' unless states.length==480
# Verify S2 reported rounded theoretical cost panels against source's aggregate cost field.
mismatches=[]
states.each_slice(20).zip(rows).each do |group,p|
  reported=Integer(p.fetch('group_stage_total_cost'))
  formula=group.sum{|x|x.last}
  mismatches << [p.fetch('session'),p.fetch('group'),p.fetch('stage'),reported,formula] if reported != formula
end
warn "Source source-reported-cost versus theoretical-formula panel mismatches (NOT repaired): #{mismatches.inspect}"
CSV.open(output,'w') do |csv|
  csv<<%w[session group stage info round n1 n2 n3 incident theoretical_group_cost]
  states.each{|v|csv<<v}
end
puts "RUBY_STAGE_EXTRACT PASS panels=#{rows.length} rounds=#{states.length} sessions=#{states.map(&:first).uniq.size} source_sha256=#{Digest::SHA256.file(source).hexdigest}"
