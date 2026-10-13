package main

// P30 — constructed partially observed 2-regime congestion automaton.
// Initial regime phase is revealed exactly once; later observations are blank.
// This is not the empirical 2017 route game or a measured transport policy.
import("encoding/json";"fmt")
type Result struct{Policy string `json:"policy"`;InitialHidden int `json:"initial_hidden"`;WarmupCost int `json:"warmup_cost"`;Cycle []int `json:"recurrent_costs"`;Mean float64 `json:"mean_cost"`;Safe bool `json:"safe_cost_192_after_first_round"`}
func run(policy string,z0 int)Result{z:=z0;mem:=z0;costs:=make([]int,20)
 for t:=0;t<20;t++{a:=0;switch policy{case "blank_constant_6":a=0;case "blank_constant_7":a=1;case "one_bit":a=mem;case "fully_observed":a=z;default:panic("policy")}
 d:=a-z;costs[t]=192+2*d*d;z=1-z;if policy=="one_bit"{mem=1-mem}}
 safe:=true;for _,c:=range costs[1:]{if c!=192{safe=false}}
 return Result{policy,z0,costs[0],costs[18:20],float64(costs[18]+costs[19])/2,safe}}
func main(){r:=[]Result{};for _,p:=range []string{"blank_constant_6","blank_constant_7","one_bit","fully_observed"}{for z:=0;z<=1;z++{r=append(r,run(p,z))}}
 b,_:=json.MarshalIndent(r,"","  ");fmt.Println(string(b))}
