package main
// Independent Go finite graph/Karp witness verification of Ruby P0-R5.
// Previous-bin shocks available only under hypothetical certified receipt.
import("fmt";"math";"math/bits")
type S struct{Q0,Q1,Active,Prev,Older,H,Mem,Blocked int}
type Edge struct{To,Cost int}
func verify(lag,bitsN,action,update int)(float64,bool,int){
 states:=[]S{};ids:=map[S]int{};edges:=[][]Edge{}
 var add func(S)int
 add=func(s S)int{if v,ok:=ids[s];ok{return v};v:=len(states);ids[s]=v;states=append(states,s);edges=append(edges,nil);return v}
 add(S{});add(S{Active:1})
 safe:=true
 for i:=0;i<len(states);i++{
  s:=states[i];obs:=0;if lag==1{obs=s.Prev};if lag==2{obs=s.Older}
  ix:=s.Mem*3+obs;cmd:=(action>>ix)&1;mem:=0;if bitsN==1{mem=(update>>ix)&1}
  for w:=0;w<=2;w++{
   shock:=0;if w>0{shock=1};if bits.OnesCount(uint(s.H))+shock>1{continue}
   x,y:=s.Q0,s.Q1;if w==1{x++};if w==2{y++}
   if s.Active==0{x--}else{y--};if x<0{x=0};if y<0{y=0}
   if x+y>2||x>2||y>2{safe=false}
   if x>2{x=2};if y>2{y=2}
   next:=S{x,y,cmd,w,s.Prev,((s.H<<1)|shock)&3,mem,0}
   dst:=add(next);cost:=4*(x+y);if cmd!=s.Active{cost++};edges[i]=append(edges[i],Edge{dst,cost})
  }
 }
 n:=len(states);dp:=make([][]float64,n+1)
 for k:=range dp{dp[k]=make([]float64,n);for j:=range dp[k]{dp[k][j]=math.Inf(-1)}}
 for i:=0;i<n;i++{dp[0][i]=0}
 for k:=1;k<=n;k++{for i:=0;i<n;i++{if math.IsInf(dp[k-1][i],-1){continue};for _,e:=range edges[i]{v:=dp[k-1][i]+float64(e.Cost);if v>dp[k][e.To]{dp[k][e.To]=v}}}}
 best:=math.Inf(-1)
 for v:=0;v<n;v++{if math.IsInf(dp[n][v],-1){continue};low:=math.Inf(1);for k:=0;k<n;k++{if math.IsInf(dp[k][v],-1){continue};ratio:=(dp[n][v]-dp[k][v])/float64(n-k);if ratio<low{low=ratio}};if low>best{best=low}}
 return best/4,safe,n
}
func main(){
 for _,c:=range []struct{lag,bits,act,upd int;want float64}{
 {0,1,1,1,7.0/12},{1,0,1,0,5.0/6},{1,1,33,3,5.0/12},{2,0,1,0,7.0/6},{2,1,1,1,0.5},
 }{v,s,n:=verify(c.lag,c.bits,c.act,c.upd);fmt.Printf("lag=%d bits=%d value=%.9f safe=%v states=%d\n",c.lag,c.bits,v,s,n);if math.Abs(v-c.want)>1e-8||!s{panic("independent Go mismatch")}}
}
