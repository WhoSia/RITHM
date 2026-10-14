package main
import("testing";"math")
func TestExactMinimaxDeclaredClasses(t *testing.T){
 for _,c:=range []struct{K,B int;Want float64}{{3,0,0},{3,1,1},{3,2,2},{5,1,.6}}{
  for mem:=0;mem<=1;mem++{r,_,_,n:=synth(c.K,c.B,mem);if math.Abs(r.Mean-c.Want)>1e-9||!r.Safe||r.Overflow{t.Fatalf("K=%d B=%d memory=%d result=%+v",c.K,c.B,mem,r)}
   if mem==0&&n!=4||mem==1&&n!=256{t.Fatalf("policy count %d",n)}
  }
 }
}
func TestBaselineCapacityViolation(t *testing.T){r:=evaluate(3,1,0,0,0);if !r.Overflow||r.Safe{t.Fatalf("expected overflow and unsafe: %+v",r)}}
func TestDelayedInputInitialNotLeakCurrentShock(t *testing.T){r:=evaluate(3,1,0,2,0);if r.Nodes<3||r.Mean!=1{t.Fatal(r)}}
