package main
import("testing";"math")
func same(a,b float64)bool{return math.Abs(a-b)<1e-8}
func TestNoShock(t *testing.T){for _,m:=range []string{"no_feedback","feedback"}{a:=solve(m,"toggle1bit",3,0);if !same(a.WorstMean,192)||!a.Safe{t.Fatal(a)}}}
func TestPersistentUncorrectedPhase(t *testing.T){for _,k:=range []int{3,5}{a:=solve("no_feedback","toggle1bit",k,1);if !same(a.WorstMean,196)||a.Safe{t.Fatal(a)}}}
func TestBudgetedFeedback(t *testing.T){for _,c:=range []struct{k,b int;v float64}{{3,1,193+1.0/3},{3,2,194+2.0/3},{3,3,196},{5,1,192.8},{5,2,193.6}}{a:=solve("feedback","toggle1bit",c.k,c.b);if !same(a.WorstMean,c.v)||a.Safe{t.Fatal(a)}}}
func TestOracle(t *testing.T){for _,m:=range []string{"no_feedback","feedback"}{for _,k:=range []int{3,5}{for b:=0;b<=k;b++{a:=solve(m,"oracle",k,b);if !same(a.WorstMean,192)||!a.Safe{t.Fatal(a)}}}}}
func TestMonotoneInShockBudget(t *testing.T){for _,m:=range []string{"no_feedback","feedback"}{for _,p:=range []string{"constant0","toggle1bit","delay1","oracle"}{prev:=0.0;for b:=0;b<=3;b++{a:=solve(m,p,3,b);if b>0&&a.WorstMean+1e-8<prev{t.Fatal(a)};prev=a.WorstMean}}}}
func TestP31NoShockRegression(t *testing.T){a:=solve("no_feedback","delay1",3,0);b:=solve("feedback","delay1",3,0);if !same(a.WorstMean,196)||!same(b.WorstMean,194){t.Fatal(a,b)}}
