package main
import("fmt";"encoding/json";"math";"math/bits")
type State struct{Z,Prev,Q,Mem,History int}
type Edge struct{To,Cost,Shock int}
type Result struct{Model,Policy string; K,B,States int; WorstMean float64; Safe bool}
func action(p string,s State)int{switch p{case "constant0":return 0;case "toggle1bit":return s.Mem;case "delay1":return s.Prev;case "oracle":return s.Z};panic(p)}
func successors(s State, model,policy string,K,B int)[]struct{To State;Cost,Shock int}{
 a:=action(policy,s);d:=a^s.Z;c:=192+2*d+2*s.Q; ans:=[]struct{To State;Cost,Shock int}{}
 for w:=0;w<=1;w++{if w+bits.OnesCount(uint(s.History))>B{continue};z:=s.Z^1^w;if model=="feedback"{z^=d};h:=0;if K>1{h=((s.History<<1)|w)&((1<<(K-1))-1)};ans=append(ans,struct{To State;Cost,Shock int}{State{z,s.Z,d,s.Mem^1,h},c,w})}
 return ans
}
func solve(model,policy string,K,B int)Result{
 if K<1||K>8||B<0||B>K{panic("bad budget")}
 states:=[]State{};ids:=map[State]int{};out:=[][]Edge{}
 var insert func(State)int
 insert=func(s State)int{if i,ok:=ids[s];ok{return i};i:=len(states);ids[s]=i;states=append(states,s);out=append(out,nil);return i}
 insert(State{Z:0,Mem:0});insert(State{Z:1,Mem:1})
 safe:=true
 for i:=0;i<len(states);i++{for _,e:=range successors(states[i],model,policy,K,B){j:=insert(e.To);out[i]=append(out[i],Edge{j,e.Cost,e.Shock});if e.Cost>192{safe=false}}}
 n:=len(states); const neg=-1e15
 dp:=make([][]float64,n+1);for i:=range dp{dp[i]=make([]float64,n);for j:=range dp[i]{dp[i][j]=neg}}
 for i:=0;i<n;i++{dp[0][i]=0}
 for k:=1;k<=n;k++{for i:=0;i<n;i++{if dp[k-1][i]==neg{continue};for _,e:=range out[i]{v:=dp[k-1][i]+float64(e.Cost);if v>dp[k][e.To]{dp[k][e.To]=v}}}}
 best:=math.Inf(-1)
 for v:=0;v<n;v++{if dp[n][v]==neg{continue};low:=math.Inf(1);for k:=0;k<n;k++{if dp[k][v]==neg{continue};r:=(dp[n][v]-dp[k][v])/float64(n-k);if r<low{low=r}};if low>best{best=low}}
 return Result{model,policy,K,B,n,best,safe}
}
func main(){a:=[]Result{};for _,model:=range []string{"no_feedback","feedback"}{for _,policy:=range []string{"constant0","toggle1bit","delay1","oracle"}{for _,kb:=range [][2]int{{3,0},{3,1},{3,2},{3,3},{5,1},{5,2}}{a=append(a,solve(model,policy,kb[0],kb[1]))}}};o,_:=json.MarshalIndent(a,"","  ");fmt.Println(string(o))}
