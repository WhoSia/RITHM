# frozen_string_literal: true
require 'json'
require_relative '../p1p7/receipt'
# Export source-independent witness for the Go replay. Synthetic evidence only.
module RithmP1P9
 def self.export(path,h:5,b:1)
  c=RithmP1P7::Contract.new(h:h,pattern: :lag1)
  s=RithmP1P7::Solver.new(h:h,budget:b,contract:c)
  raise 'unsatisfiable' unless s.solve
  worlds=[Array.new(h,0)]+h.times.map{|i|Array.new(h){|j|i==j ? 1 : 0}}
  nodes={}
  traverse=nil
  traverse=lambda{|t,rs,last,trained,spent|
   return if t==h
   k=[t,rs,last,trained,spent]
   who,boost=s.policy.fetch(k)
   change=last!=2&&last!=who
   nexts=rs.map{|i,a,z|
    cap=[0,1+boost-worlds[i][t]-(change&&trained==0 ? 1 : 0)].max
    who==0 ? [i,[2,a+cap].min,z] : [i,a,[2,z+cap].min]
   }
   groups=nexts.group_by{|i,_,_|c.observation(t+1,worlds[i])}
   nodes[JSON.generate(k)]={'action'=>[who,boost],'children'=>groups.map{|obs,g|
    nk=[t+1,g,who,trained|(change ? 1 : 0),spent+boost]
    traverse.call(*nk)
    {'observation'=>obs,'key'=>JSON.generate(nk)}
   }}
  }
  root=[0,worlds.each_index.map{|i|[i,0,0]},2,0,0]
  traverse.call(*root)
  records=c.events.map{|x|{'id'=>x.event,'published'=>x.published,'received'=>x.received,'trusted'=>x.certified}}
  File.write(path,JSON.pretty_generate({'schema'=>'rithm.p1p9.policy.v1','horizon'=>h,'boost_budget'=>b,'records'=>records,'root'=>JSON.generate(root),'nodes'=>nodes}))
  nodes.length
 end
end
if __FILE__==$PROGRAM_NAME
 puts "exported #{RithmP1P9.export(ARGV.fetch(0,'policy.json'))} nodes"
end