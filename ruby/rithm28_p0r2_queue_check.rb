require 'set'
def check(k,b)
 states=[[0,0,0],[0,1,0]];ids=states.each_with_index.to_h;edges=[];i=0;overflow=false
 while i<states.size
  q,p,h=states[i];a=p;edges[i]=[]
  (0..1).each do |w|
   next if h.to_s(2).count('1')+w>b
   raw=q+w-a;overflow||=raw>4
   nq=[[raw,0].max,4].min
   nh=k>1 ? (((h<<1)|w)&((1<<(k-1))-1)) : 0
   st=[nq,w,nh]
   unless ids.key?(st);ids[st]=states.size;states<<st;end
   edges[i]<<[ids[st],nq+2*a]
  end
  i+=1
 end
 best=0.0
 walk=nil
 walk=lambda{|root,cur,seen,sum,n|
  edges[cur].each{|to,c|
   if to==root;best=[best,(sum+c).to_f/(n+1)].max
   elsif !seen.include?(to)
    seen.add(to);walk.call(root,to,seen,sum+c,n+1);seen.delete(to)
   end
  }
 }
 states.each_index{|r|walk.call(r,r,Set[r],0,0)}
 [best,overflow]
end
{[3,0]=>0.0,[3,1]=>1.0,[3,2]=>2.0,[5,1]=>0.6}.each{|kb,x|
 r=check(*kb);raise "failure #{kb}" unless (r[0]-x).abs<1e-10&&!r[1]
 puts "PASS #{kb} #{r[0]}"
}
