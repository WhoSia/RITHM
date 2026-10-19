package main
import("encoding/json";"fmt")
type Row struct {Policies []string `json:"policies"`; Individual []int `json:"individual_quarters"`; Social int `json:"social_quarters"`; Nash bool `json:"pure_nash"`}
func payoff(a,b,z int)(int,int){r:=[]int{0,0};if a==1 {r[0]=z};if b==1 {r[1]=z};n:=[]int{0,0};for _,v:=range r{n[v]++};loss:=[]int{0,0};for i,x:=range r{loss[i]=n[x]*4;if x!=z{loss[i]+=8}};if a==1{loss[0]+=4};if b==1{loss[1]+=4};return loss[0],loss[1]}
func expected(a,b int)(int,int){x,y:=payoff(a,b,0);u,v:=payoff(a,b,1);return (x+u)/2,(y+v)/2}
func main(){rows:=[]Row{};for a:=0;a<2;a++{for b:=0;b<2;b++{x,y:=expected(a,b);dx,_:=expected(1-a,b);_,dy:=expected(a,1-b);names:=[]string{"stop","compute"};rows=append(rows,Row{[]string{names[a],names[b]},[]int{x,y},x+y,dx>=x&&dy>=y})}};data,_:=json.Marshal(rows);fmt.Println(string(data))}
