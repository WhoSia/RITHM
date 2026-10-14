package main
import ("fmt";"math";"math/bits")
type S struct{Q,P,M,H int}
type E struct{To,Cost int}
type R struct{Mean float64;Safe,Overflow bool;Nodes int}
// 5-minute CONSTRUCTED model. Prior arrival P is observable only IF
// provider release and client receipt before this service decision are certified.
// Arrivals=1+w, service=1+a, cost=q(next)+2a vehicle-equivalent/5min.
func evaluate(k,b,mem,act,upd int) R {
 states:=[]S{};ids:=map[S]int{};edges:=[][]E{}
 var add func(S)int
 add=func(s S)int{if id,ok:=ids[s];ok{return id};id:=len(states);ids[s]=id;states=append(states,s);edges=append(edges,nil);return id}
 add(S{P:0});add(S{P:1})
 safe,overflow:=true,false
 for i:=0;i<len(states);i++{s:=states[i];a:=(act>>(2*s.M+s.P))&1;m:=0;if mem==1{m=(upd>>(2*s.M+s.P))&1}
  for w:=0;w<=1;w++{if bits.OnesCount(uint(s.H))+w>b{continue}
   raw:=s.Q+w-a;q:=raw;if q<0{q=0};if q>4{q=4;overflow=true};if q>2{safe=false}
   h:=0;if k>1{h=((s.H<<1)|w)&((1<<(k-1))-1)}
   j:=add(S{q,w,m,h});edges[i]=append(edges[i],E{j,q+2*a})
  }
 }
 n:=len(states);dp:=make([][]float64,n+1)
 for t:=range dp{dp[t]=make([]float64,n);for i:=range dp[t]{dp[t][i]=-1e18}}
 for i:=0;i<n;i++{dp[0][i]=0}
 for t:=1;t<=n;t++{for i:=0;i<n;i++{if dp[t-1][i]<0{continue};for _,e:=range edges[i]{v:=dp[t-1][i]+float64(e.Cost);if v>dp[t][e.To]{dp[t][e.To]=v}}}}
 best:=math.Inf(-1)
 for v:=0;v<n;v++{low:=math.Inf(1);for t:=0;t<n;t++{if dp[t][v]<0{continue};x:=(dp[n][v]-dp[t][v])/float64(n-t);if x<low{low=x}};if low>best{best=low}}
 return R{best,safe,overflow,n}
}
func synth(k,b,mem int)(R,int,int,int) {
 best:=R{Mean:math.Inf(1)};bestA,bestU,count:=0,0,0
 maxA,maxU:=4,1;if mem==1{maxA,maxU=16,16}
 for a:=0;a<maxA;a++{for u:=0;u<maxU;u++{r:=evaluate(k,b,mem,a,u);count++;if r.Mean<best.Mean-1e-9||(math.Abs(r.Mean-best.Mean)<1e-9&&r.Safe&&!best.Safe){best,bestA,bestU=r,a,u}}}
 return best,bestA,bestU,count
}
func main(){for _,p:=range [][2]int{{3,0},{3,1},{3,2},{5,1}}{for mem:=0;mem<=1;mem++{r,a,u,n:=synth(p[0],p[1],mem);fmt.Printf("K%d B%d memory%d tried%d mean%.6f safe%v overflow%v act%d upd%d states%d\n",p[0],p[1],mem,n,r.Mean,r.Safe,r.Overflow,a,u,r.Nodes)}}}
