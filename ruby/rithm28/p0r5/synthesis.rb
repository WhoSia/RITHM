# frozen_string_literal: true
# RITHM 2.8 P0-R5: Ruby-first full 1-bit Mealy synthesis.
# Synthetic 5-minute two-queue network, NOT measured human/field welfare.
require 'json'
class R5
 def initialize(lag:,act:,update:,bits:,spill:false,k:3,b:1)
  @lag,@act,@upd,@bits,@spill,@k,@b=lag,act,update,bits,spill,k,b
 end
 def evaluate
  states=[];id={};edges=[];unsafe=false;overflow=false;spilled=false
  put=lambda{|s|id.fetch(s){i=states.size;id[s]=i;states<<s;edges<<[];i}}
  [0,1].each{|a|put.call([0,0,a,0,0,0,0,0])}
  i=0
  while i<states.size
   q0,q1,active,prev,older,h,mem,blocked=states[i]
   obs=@lag==1 ? prev : (@lag==2 ? older : -1)
   input=obs<0 ? 0 : obs
   ix=mem*3+input
   command=(@act>>ix)&1
   nextmem=@bits==0 ? 0 : ((@upd>>ix)&1)
   edges[i]=[]
   [0,1,2].each do |w|
    event=w==0 ? 0 : 1
    next if h.to_s(2).count('1')+event>@b
    x=q0+(w==1 ? 1 : 0)-(active==0 ? 1 : 0)
    y=q1+(w==2 ? 1 : 0)-(active==1 ? 1 : 0)
    x=[x,0].max;y=[y,0].max
    lost=[x-2,0].max+[y-2,0].max
    overflow||=lost>0
    unsafe||=(x+y>2||lost>0)
    x=[x,2].min;y=[y,2].min
    nb=@spill ? [blocked+lost,2].min : 0
    spilled||=lost>0
    nh=((h<<1)|event)&3
    j=put.call([x,y,command,w,prev,nh,nextmem,nb])
    cost=4*(x+y)+(command==active ? 0 : 1)
    cost+=16*lost+8*nb if @spill
    edges[i]<<[j,cost]
   end
   i+=1
  end
  n=states.size
  last=Array.new(n,0);dp=[last]
  n.times do
   current=Array.new(n,-Float::INFINITY)
   edges.each_with_index{|es,u|es.each{|v,c|z=last[u]+c;current[v]=z if z>current[v]}}
   dp<<current;last=current
  end
  mean=(0...n).filter_map{|v|
   next unless dp[n][v].finite?
   (0...n).filter_map{|t|(dp[n][v]-dp[t][v]).fdiv(n-t) if dp[t][v].finite?}.min
  }.max/4.0
  [mean,!unsafe,overflow,n,spilled]
 end
end
def rithm28_p0r5_synth(lag,spill=false)
 best={};count=0;safe_count=0
 [0,1].each do |bits|
  max_action=bits==0 ? 8 : 64
  max_update=bits==0 ? 1 : 64
  max_action.times do |act|
   max_update.times do |update|
    value,safe,overflow,n,_=R5.new(lag:lag,act:act,update:update,bits:bits,spill:spill).evaluate
    count+=1;safe_count+=1 if safe
    if safe && (!best[bits]||value<best[bits][:value]-1e-10)
     best[bits]={value:value,action:act,update:update,states:n,overflow:overflow}
    end
   end
  end
 end
 {lag:lag,spill:spill,count:count,safe_count:safe_count,best:best}
end
if __FILE__==$0
 [0,1,2].each{|lag|[false,true].each{|spill|puts JSON.generate(rithm28_p0r5_synth(lag,spill))}}
end
