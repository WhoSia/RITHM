package main
import "testing"
func TestBaselineP24(t *testing.T){s:=state{n1:4,n2:4,n3:4,z:0};if cost(4,4,0)!=212{t.Fatal("baseline")};lo,hi:=bounds(s,1,"unrestricted");if lo!=-8||hi!=6{t.Fatalf("got %d %d",lo,hi)}}
func TestIncidentAvoidNoHarmExhaustive(t *testing.T){for n1:=0;n1<=12;n1++{for n2:=0;n2<=12-n1;n2++{s:=state{n1:n1,n2:n2,n3:12-n1-n2,z:1};for k:=0;k<=2;k++{lo,_:=bounds(s,k,"incident_avoid");if lo!=0{t.Fatalf("incident avoidance harmed %d/%d k=%d",n1,n2,k)}}}}}
func TestSourceBounds(t *testing.T){states,e:=readStates("../results/2017_group_states_derived.csv");if e!=nil{t.Fatal(e)};r:=run(states,"unrestricted",1);if r.BothSigns!=369||r.BenefitFeasible!=376||r.HarmFeasible!=472{t.Fatalf("%+v",r)};r=run(states,"incident_avoid",1);if r.HarmFeasible!=0||r.BenefitFeasible!=46{t.Fatal(r)}}
func TestNoSwitchSubset(t *testing.T){s:=state{n1:6,n2:0,n3:6,z:1};lo,hi:=bounds(s,1,"incident_avoid");if lo!=0||hi!=0{t.Fatal("no C-B entrant should not switch off C-B")}}
