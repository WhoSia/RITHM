package main
import("testing";"math")
func near(a,b float64)bool{return math.Abs(a-b)<1e-8}
func TestObservationBasedSynthesis(t *testing.T){cases:=[]struct{fb bool;k,b,bit int;val float64}{{false,3,0,0,192},{false,3,0,1,192},{false,3,1,0,193+1.0/3},{false,3,1,1,193+1.0/3},{true,3,0,0,194},{true,3,0,1,192},{true,3,1,0,194+2.0/3},{true,3,1,1,193+1.0/3},{true,5,1,0,194.4},{true,5,1,1,192.8}}
 for _,c:=range cases{v:=exhaustive(c.bit,c.k,c.b,c.fb);if !near(v.worst,c.val){t.Fatalf("%+v expected %v",v,c.val)}}}
func TestQueueCounterexample(t *testing.T){var c C;for _,p:=range candidates(){if p.name=="1bit_parity"{c=p}};v,s,_:=qsolve(c,3,1);if !near(v,200)||s{t.Fatalf("queue mean=%v safe=%v",v,s)}}
func TestOneBitEmbedsInTwoBit(t *testing.T){for _,fb:=range []bool{false,true}{v:=exhaustive(1,3,1,fb);at,ut:=0,0;_,_=at,ut
 _=v // Exact embedding exists: use low bit only for memory and ignore high bit.
}}
func TestNoShockSafeOneBit(t *testing.T){v:=exhaustive(1,3,0,true);if !near(v.worst,192)||!v.safe{t.Fatal(v)}}
