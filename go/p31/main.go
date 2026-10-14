package main
import("fmt";"encoding/json")
type State struct{ Z,Prev,Q,Mem int }
type Finding struct{ Model,Policy string; States int; MaxMean float64; Safe bool }
func act(p string,s State)int{switch p{case "constant0":return 0;case "toggle1bit":return s.Mem;case "delay1":return s.Prev;case "oracle":return s.Z};panic(p)}
type Transition struct{ To State; Cost int }
func nexts(model,p string,s State)[]Transition{
 a:=act(p,s);d:=a^s.Z;c:=192+2*d+2*s.Q;ws:=[]int{0}
 if model=="shock_only"||model=="shock_feedback"{ws=[]int{0,1}}
 res:=[]Transition{}
 for _,w:=range ws{z:=s.Z^1^w;if model=="feedback_only"||model=="shock_feedback"{z^=d};res=append(res,Transition{State{z,s.Z,d,s.Mem^1},c})}
 return res
}
func solve(model,p string)Finding{
 states:=[]State{};ids:=map[State]int{};edges:=[][]struct{To,Cost int}{}
 add:=func(s State)int{return 0};_ = add
 var push func(State)int
 push=func(s State)int{if v,ok:=ids[s];ok{return v};k:=len(states);ids[s]=k;states=append(states,s);edges=append(edges,nil);return k}
 push(State{0,0,0,0});push(State{1,0,0,1})
 safe:=true
 for i:=0;i<len(states);i++{for _,t:=range nexts(model,p,states[i]){k:=push(t.To);edges[i]=append(edges[i],struct{To,Cost int}{k,t.Cost});if t.Cost>192{safe=false}}}
 worst:=0.0
 var dfs func(start,at int,seen []bool,depth,sum int)
 dfs=func(start,at int,seen []bool,depth,sum int){for _,e:=range edges[at]{if e.To==start{v:=float64(sum+e.Cost)/float64(depth);if v>worst{worst=v}}else if !seen[e.To]{seen[e.To]=true;dfs(start,e.To,seen,depth+1,sum+e.Cost);seen[e.To]=false}}}
 for i:=range states{used:=make([]bool,len(states));used[i]=true;dfs(i,i,used,1,0)}
 return Finding{model,p,len(states),worst,safe}
}
func main(){ans:=[]Finding{};for _,m:=range []string{"clock_only","feedback_only","shock_only","shock_feedback"}{for _,p:=range []string{"constant0","toggle1bit","delay1","oracle"}{ans=append(ans,solve(m,p))}};b,_:=json.MarshalIndent(ans,"","  ");fmt.Println(string(b))}
