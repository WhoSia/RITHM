package main
import("encoding/json";"fmt")
// A deliberately small CONSTRUCTED two-route congestion automaton.
// NOT fitted to the empirical 2017 three-route experiment.
const N=12
func cost(x int) int {d:=x-6;return 192+2*d*d}
func stepNaive(x int) int {if x<=6{return x+1};return x-1}
func stepGuarded(x int) int {if x<6{return x+1};if x>6{return x-1};return x}
type Verdict struct {Policy string `json:"policy"`;Initial int `json:"initial"`;Prefix []int `json:"prefix"`;Cycle []int `json:"cycle"`;CycleCostSum int `json:"cycle_cost_sum"`;CycleLen int `json:"cycle_length"`}
func analyze(policy string,initial int,f func(int)int) Verdict {seen:=map[int]int{};trace:=[]int{};x:=initial
 for {if at,ok:=seen[x];ok{cy:=append([]int{},trace[at:]...);tot:=0;for _,z:=range cy{tot+=cost(z)};return Verdict{policy,initial,append([]int{},trace[:at]...),cy,tot,len(cy)}};seen[x]=len(trace);trace=append(trace,x);x=f(x);if x<0||x>N{panic("invalid occupancy")}}}
func main(){v:=[]Verdict{};for x:=0;x<=N;x++ {v=append(v,analyze("naive<=6_up",x,stepNaive),analyze("guarded_stop_at_6",x,stepGuarded))};buf,_:=json.MarshalIndent(v,"","  ");fmt.Println(string(buf))}
