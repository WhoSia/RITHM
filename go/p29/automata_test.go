package main
import "testing"
func TestAllInitialStates(t *testing.T){for x:=0;x<=N;x++ {a:=analyze("naive",x,stepNaive);b:=analyze("guarded",x,stepGuarded);if a.CycleCostSum!=386||a.CycleLen!=2 {t.Fatalf("naive wrong x=%d: %+v",x,a)};if b.CycleCostSum!=192||b.CycleLen!=1||b.Cycle[0]!=6{t.Fatalf("guarded wrong x=%d: %+v",x,b)}}}
func TestCost(t *testing.T){if cost(6)!=192||cost(7)!=194||cost(0)!=264||cost(12)!=264{t.Fatal("cost values")}}
