package main
import ("math";"math/bits";"fmt")
type S33 struct{Z,Prev,Q,H,Mem int}
type Policy33 struct{Name string;Bits int;Act func(S33)int;Upd func(S33)int}
type E33 struct{To,Cost int}
func solve33(p Policy33,k,b int,queue,feedback bool)(float64,bool,int){
 states:=[]S33{};ids:=map[S33]int{};edge:=[][]E33{}
 var put func(S33)int
 put=func(s S33)int{if id,ok:=ids[s];ok{return id};id:=len(states);ids[s]=id;states=append(states,s);edge=append(edge,nil);return id}
 for z:=0;z<=1;z++{initial:=z;if p.Bits==0{initial=0};put(S33{Z:z,Prev:z,Mem:initial})}
 safe:=true
 for i:=0;i<len(states);i++{
  s:=states[i];a:=p.Act(s);d:=a^s.Z;c:=192+2*d+2*s.Q
  if c>192{safe=false}
  nq:=d
  if queue{nq=s.Q+2*d-1;if nq<0{nq=0};if nq>3{nq=3}}
  for w:=0;w<=1;w++{if bits.OnesCount(uint(s.H))+w>b{continue}
   z:=s.Z^1^w;if feedback{z^=d}
   h:=0;if k>1{h=((s.H<<1)|w)&((1<<(k-1))-1)}
   mem:=p.Upd(s)&((1<<p.Bits)-1)
   j:=put(S33{Z:z,Prev:s.Z,Q:nq,H:h,Mem:mem})
   edge[i]=append(edge[i],E33{j,c})
  }
 }
 n:=len(states);dp:=make([][]float64,n+1)
 for t:=range dp{dp[t]=make([]float64,n);for i:=range dp[t]{dp[t][i]=-1e15}}
 for i:=0;i<n;i++{dp[0][i]=0}
 for t:=1;t<=n;t++{for i:=0;i<n;i++{if dp[t-1][i]<0{continue};for _,e:=range edge[i]{v:=dp[t-1][i]+float64(e.Cost);if v>dp[t][e.To]{dp[t][e.To]=v}}}}
 best:=math.Inf(-1)
 for v:=0;v<n;v++{lo:=math.Inf(1);for t:=0;t<n;t++{if dp[t][v]<0{continue};x:=(dp[n][v]-dp[t][v])/float64(n-t);if x<lo{lo=x}};if lo>best{best=lo}}
 return best,safe,n
}
type Winner33 struct{Bits,K,B int;Feedback bool;Name string;Worst float64;Safe bool}
func synth33(bitsN,k,b int,feedback bool)Winner33{
 best:=Winner33{Bits:bitsN,K:k,B:b,Feedback:feedback,Worst:math.Inf(1)}
 M:=1<<bitsN;numAct:=1<<(2*M);numUpdate:=1;if bitsN==1{numUpdate=1<<(2*M)}
 for at:=0;at<numAct;at++{for ut:=0;ut<numUpdate;ut++{
  actionTable,updateTable:=at,ut
  p:=Policy33{Name:fmt.Sprintf("act=%d,update=%d",at,ut),Bits:bitsN,
  Act:func(s S33)int{return(actionTable>>(2*s.Mem+s.Prev))&1},
  Upd:func(s S33)int{if bitsN==0{return 0};return(updateTable>>(2*s.Mem+s.Prev))&1}}
  v,safe,_:=solve33(p,k,b,false,feedback)
  if v<best.Worst-1e-9||(math.Abs(v-best.Worst)<1e-9&&safe&&!best.Safe){best.Name=p.Name;best.Worst=v;best.Safe=safe}
 }}
 return best
}
func parity33()Policy33{return Policy33{Name:"one-bit-parity",Bits:1,Act:func(s S33)int{return s.Mem},Upd:func(s S33)int{return s.Mem^1}}}
func queue33(k,b int)(float64,bool){v,s,_:=solve33(parity33(),k,b,true,false);return v,s}
