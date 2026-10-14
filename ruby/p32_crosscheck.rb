# Independent P32 maximum-cycle check by simple-cycle DFS, not Karp.
require "json"
def brute(k,b,feedback)
 nodes=[[0,0,0,0,0],[1,0,0,1,0]]
 ids={};nodes.each_with_index{|s,i|ids[s]=i};edges=[];i=0
 while i<nodes.size
  z,prev,q,mem,h=nodes[i];a=mem;d=a^z;cost=192+2*d+2*q;edges[i]=[]
  (0..1).each do |w|
   next if h.to_s(2).count("1")+w>b
   nz=z^1^w^(feedback ? d : 0)
   nh=k>1 ? (((h<<1)|w)&((1<<(k-1))-1)) : 0
   dst=[nz,z,d,mem^1,nh]
   unless ids.key?(dst);ids[dst]=nodes.size;nodes << dst;end
   edges[i] << [ids[dst],cost]
  end
  i+=1
 end
 best=0.0
 visit=nil
 visit=lambda do |root,cur,seen,sum,length|
  edges[cur].each do |dest,c|
   if dest==root
    best=[best,(sum+c).to_f/(length+1)].max
   elsif !seen[dest]
    seen[dest]=true;visit.call(root,dest,seen,sum+c,length+1);seen.delete(dest)
   end
  end
 end
 nodes.each_index{|root|visit.call(root,root,{root=>true},0,0)}
 [nodes.length,best]
end
checks={}
[[3,0],[3,1],[3,2],[5,1]].each{|k,b|[false,true].each{|f|checks["#{k}-#{b}-#{f}"]=brute(k,b,f)}}
raise "budget one/no feedback mismatch" unless checks["3-1-false"]==[13,196.0]
raise "budget one/feedback mismatch" unless (checks["3-1-true"][1]-193.3333333333).abs<1e-8
puts JSON.pretty_generate(checks)
