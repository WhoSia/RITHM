# frozen_string_literal: true
require 'json'
require 'digest'
module RithmP1P10
 module_function
 def worlds(h)
  [Array.new(h,0)]+h.times.map{|i|Array.new(h){|j|i==j ? 1 : 0}}
 end
 def evidence(h,lag:4,publish_delay:1)
  h.times.map{|id|{'id'=>id,'published'=>id+publish_delay,'received'=>id+lag,'trusted'=>true}}
 end
 def validate!(records,h)
  raise 'event count' unless records.length==h
  raise 'event identifiers' unless records.map{|r|r.fetch('id')}.sort==(0...h).to_a
  records.each{|r|raise 'invalid publication/receipt order' unless r.fetch('id')<r.fetch('published')&&r.fetch('published')<=r.fetch('received')}
  true
 end
 def observation(records,t,w)
  records.select{|r|r.fetch('trusted')&&r.fetch('received')==t}.map{|r|[r.fetch('id'),w.fetch(r.fetch('id'))]}.sort
 end
 def trace(records,world,h)
  (0..h).map{|t|observation(records,t,world)}
 end
 def same_observation?(left,right,h)
  validate!(left,h);validate!(right,h)
  worlds(h).all?{|w|trace(left,w,h)==trace(right,w,h)}
 end
 def provenance_digest(records)
  Digest::SHA256.hexdigest(JSON.generate(records))
 end
 def report(h:5)
  a=evidence(h,lag:4,publish_delay:1)
  b=evidence(h,lag:4,publish_delay:2)
  c=evidence(h,lag:4,publish_delay:1).map(&:dup)
  c[0]['received']=3
  {'h'=>h,'worlds'=>worlds(h).length,'published_shift_observation_equivalent'=>same_observation?(a,b,h),
   'published_shift_distinct_digest'=>provenance_digest(a)!=provenance_digest(b),
   'earlier_receipt_observation_equivalent'=>same_observation?(a,c,h),'synthetic_only'=>true}
 end
end
puts JSON.pretty_generate(RithmP1P10.report) if $PROGRAM_NAME==__FILE__
