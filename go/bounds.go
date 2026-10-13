// RITHM-2.7 P27 source-conditional, exact finite response envelopes.
// No advice receipt, compliance or causal welfare is measured here.
package main
import (
 "encoding/csv"
 "encoding/json"
 "fmt"
 "os"
 "strconv"
)
type state struct { n1,n2,n3,z,info int; session string }
type groupSummary struct { N, BothSigns, BenefitFeasible, HarmFeasible int; LowerSum, UpperSum int }
type result struct {
 Scheme string `json:"scheme"`
 K int `json:"max_switched_eligible_c"`
 N int `json:"n_group_rounds"`
 BothSigns int `json:"both_signs_feasible"`
 BenefitFeasible int `json:"benefit_feasible"`
 HarmFeasible int `json:"harm_feasible"`
 MeanLower float64 `json:"mean_sharp_lower_cost_gain"`
 MeanUpper float64 `json:"mean_sharp_upper_cost_gain"`
 ByAccident map[string]groupSummary `json:"by_incident"`
 ByArm map[string]groupSummary `json:"by_arm"`
}
func cost(n1,n2,z int) int {return 264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2}
func bounds(s state,k int,scheme string)(int,int){
 q:=s.n2+s.n3; lo,hi:=s.n2,s.n2
 switch scheme {
 case "unrestricted": lo=max(0,s.n2-k);hi=min(q,s.n2+k)
 case "incident_avoid": if s.z==1 {lo=max(0,s.n2-k)}
 case "state_direction": if s.z==1 {lo=max(0,s.n2-k)} else {hi=min(q,s.n2+k)}
 default: panic("unknown scheme")
 }
 baseline:=cost(s.n1,s.n2,s.z);low,high:=0,0
 for c2:=lo;c2<=hi;c2++ {gain:=baseline-cost(s.n1,c2,s.z);if gain<low{low=gain};if gain>high{high=gain}}
 return low,high
}
func add(g *groupSummary,lo,hi int){g.N++;g.LowerSum+=lo;g.UpperSum+=hi;if lo<0{g.HarmFeasible++};if hi>0{g.BenefitFeasible++};if lo<0&&hi>0{g.BothSigns++}}
func readStates(path string)([]state,error){f,e:=os.Open(path);if e!=nil{return nil,e};defer f.Close();records,e:=csv.NewReader(f).ReadAll();if e!=nil{return nil,e};if len(records)!=481{return nil,fmt.Errorf("expected 480 rows, got %d",len(records)-1)}
 h:=records[0];wanted:=[]string{"session","group","stage","info","round","n1","n2","n3","incident","theoretical_group_cost"};for i,v:=range wanted{if h[i]!=v{return nil,fmt.Errorf("column %d expected %s got %s",i,v,h[i])}}
 var states []state
 for _,r:=range records[1:] {val:=func(i int)int{v,err:=strconv.Atoi(r[i]);if err!=nil{panic(err)};return v};s:=state{n1:val(5),n2:val(6),n3:val(7),z:val(8),info:val(3),session:r[0]};if s.n1+s.n2+s.n3!=12||s.z<0||s.z>1||s.info<0||s.info>1||cost(s.n1,s.n2,s.z)!=val(9){return nil,fmt.Errorf("source row invalid: %v",r)};states=append(states,s)}
 return states,nil
}
func run(states []state,scheme string,k int) result {r:=result{Scheme:scheme,K:k,N:len(states),ByAccident:map[string]groupSummary{},ByArm:map[string]groupSummary{}}
 all:=groupSummary{};for _,s:=range states {lo,hi:=bounds(s,k,scheme);add(&all,lo,hi);ak:=strconv.Itoa(s.z);a:=r.ByAccident[ak];add(&a,lo,hi);r.ByAccident[ak]=a;bk:=strconv.Itoa(s.info);b:=r.ByArm[bk];add(&b,lo,hi);r.ByArm[bk]=b}
 r.BothSigns=all.BothSigns;r.BenefitFeasible=all.BenefitFeasible;r.HarmFeasible=all.HarmFeasible;r.MeanLower=float64(all.LowerSum)/float64(all.N);r.MeanUpper=float64(all.UpperSum)/float64(all.N);return r
}
func main(){if len(os.Args)!=2{fmt.Fprintln(os.Stderr,"usage: go run go/bounds.go derived_states.csv");os.Exit(2)};s,e:=readStates(os.Args[1]);if e!=nil{panic(e)};var rr []result
 for _,scheme:=range []string{"unrestricted","incident_avoid","state_direction"}{for _,k:=range []int{0,1,2}{rr=append(rr,run(s,scheme,k))}}
 b,_:=json.MarshalIndent(rr,"","  ");fmt.Println(string(b))
}
