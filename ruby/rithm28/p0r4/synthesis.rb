# frozen_string_literal: true
# RITHM-2.8 P0-R4: Ruby-first finite observation/controller court.
# All quantities constructed; previous-bin event assumed legally received.
require 'json'
class RithmQueue
 attr_reader :states,:edges,:unsafe,:overflow
 def initialize(policy,delay=true)
  @states=[];@edges=[];@id={};@unsafe=false;@overflow=false
  [0,1].each{|a|add([0,0,a,0,0,0])}
  i=0
  while i<@states.size
   q0,q1,active,prev,h,m=@states[i]
   cmd,nm=policy.call(prev,m);effective=delay ? active : cmd;@edges[i]=[]
   [0,1,2].each do |w|
    event=w==0 ? 0 : 1
    next if h.to_s(2).count('1')+event>1
    x=[0,q0+(w==1 ? 1 : 0)-(effective==0 ? 1 : 0)].max
    y=[0,q1+(w==2 ? 1 : 0)-(effective==1 ? 1 : 0)].max
    @overflow=true if x>2||y>2
    @unsafe=true if x+y>2||x>2||y>2
    x=[x,2].min;y=[y,2].min
    j=add([x,y,cmd,w,((h<<1)|event)&3,nm])
    @edges[i]<<[j,4*(x+y)+(cmd==active ? 0 : 1)]
   end
   i+=1
  end
 end
 def add(s)
  return @id[s] if @id.key?(s)
  i=@states.size;@id[s]=i;@states<<s;@edges<<[];i
 end
 def mean
  n=@states.size;last=Array.new(n,0);dp=[last]
  n.times do
   now=Array.new(n,-Float::INFINITY)
   @edges.each_with_index{|es,i|es.each{|j,c|v=last[i]+c;now[j]=v if v>now[j]}}
   dp<<now;last=now
  end
  (0...n).filter_map{|j|
   next unless dp[n][j].finite?
   (0...n).filter_map{|t|(dp[n][j]-dp[t][j]).fdiv(n-t) if dp[t][j].finite?}.min
  }.max/4.0
 end
end
UPDATES={hold:->(p,m){m},toggle:->(p,m){m^1},
sticky:->(p,m){p==0 ? m : p-1},forget:->(p,m){0}}.freeze
def p0(table);->(obs,m){[(table>>obs)&1,0]};end
def p1(table,update);->(obs,m){[(table>>(3*m+obs))&1,UPDATES.fetch(update).call(obs,m)]};end
def synth(delay)
 all=[]
 8.times{|a|all<<[0,a,'none',p0(a)]}
 UPDATES.each_key{|u|64.times{|a|all<<[1,a,u.to_s,p1(a,u)]}}
 result=all.map{|bits,a,u,p|q=RithmQueue.new(p,delay);{bits:bits,action:a,update:u,value:q.mean,safe:!q.unsafe,overflow:q.overflow,nodes:q.states.size}}
 safe=result.select{|r|r[:safe]}
 {delay:delay,count:result.size,safe_count:safe.size,
 zero:safe.select{|r|r[:bits]==0}.min_by{|r|r[:value]},
 one:safe.select{|r|r[:bits]==1}.min_by{|r|r[:value]}}
end
if $PROGRAM_NAME==__FILE__;puts JSON.pretty_generate([synth(false),synth(true)]);end
