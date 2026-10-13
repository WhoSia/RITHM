package main
import "testing"
func TestMemorylessBound(t *testing.T){for z:=0;z<2;z++{for _,p:=range []string{"blank_constant_6","blank_constant_7"}{r:=run(p,z);if r.Mean!=193||r.Safe{t.Fatalf("memoryless: %+v",r)}}}}
func TestOneBitUpperAndSafety(t *testing.T){for z:=0;z<2;z++{r:=run("one_bit",z);if r.Mean!=192||!r.Safe{t.Fatalf("onebit: %+v",r)}}}
func TestPerfectInformationControl(t *testing.T){for z:=0;z<2;z++{r:=run("fully_observed",z);if r.Mean!=192||!r.Safe{t.Fatalf("oracle %+v",r)}}}
func TestRegimeAndCosts(t *testing.T){for _,p:=range []string{"blank_constant_6","blank_constant_7","one_bit"}{for z:=0;z<2;z++{r:=run(p,z);if r.WarmupCost!=192&&r.WarmupCost!=194{t.Fatal(r)};for _,c:=range r.Cycle{if c!=192&&c!=194{t.Fatal(r)}}}}}
func TestAllTwoMemoryControllerSynthesis(t *testing.T){total,opt,safe:=enumerate();t.Logf("machines=%d optimum=%d safe=%d",total,opt,safe);if total!=64||opt!=2||safe!=2{t.Fatalf("counts total=%d opt=%d safe=%d",total,opt,safe)};m:=Machine{Act:2,Next:1,Init:2};for z:=0;z<2;z++{v,s:=value(m,z);if v!=192||!s{t.Fatalf("candidate z=%d value=%f safe=%v",z,v,s)}}}
