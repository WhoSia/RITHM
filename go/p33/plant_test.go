package main
import("math";"testing")
func approx33(a,b float64)bool{return math.Abs(a-b)<1e-8}
func TestP33ExhaustiveMemorylessAndOneBit(t *testing.T){
 table:=[]struct{fb bool;k,b,bit int;want float64}{
 {false,3,0,0,192},{false,3,0,1,192},
 {false,3,1,0,193+1.0/3},{false,3,1,1,193+1.0/3},
 {false,5,1,0,192.8},{false,5,1,1,192.8},
 {true,3,0,0,194},{true,3,0,1,192},
 {true,3,1,0,194+2.0/3},{true,3,1,1,193+1.0/3},
 {true,5,1,0,194.4},{true,5,1,1,192.8}}
 for _,c:=range table{v:=synth33(c.bit,c.k,c.b,c.fb);if !approx33(v.Worst,c.want){t.Fatalf("%+v expected %.6f",v,c.want)}}
}
func TestP33CappedAdditiveQueue(t *testing.T){v,s:=queue33(3,1);if !approx33(v,200)||s{t.Fatalf("queue=%f safe=%v",v,s)}}
func TestP33NoShockSafeOneBit(t *testing.T){v:=synth33(1,3,0,true);if !approx33(v.Worst,192)||!v.Safe{t.Fatal(v)}}
func TestP33ExactFiniteGraph(t *testing.T){c:=parity33();for _,fb:=range []bool{false,true}{for _,k:=range []int{3,5}{for b:=0;b<=1;b++{v,_,n:=solve33(c,k,b,false,fb);if n<2||v<192||v>196{t.Fatal(n,v)}}}}}
func TestP33TwoBitEmbedding(t *testing.T){
 p:=Policy33{Name:"lift1to2",Bits:2,Act:func(s S33)int{return s.Mem&1},Upd:func(s S33)int{return(s.Mem&1)^1}}
 q:=parity33()
 for _,fb:=range []bool{false,true}{a,_,_:=solve33(p,3,1,false,fb);b,_,_:=solve33(q,3,1,false,fb);if !approx33(a,b){t.Fatal(a,b)}}
}

func TestP33StructuredTwoBitExhaustion(t *testing.T){
 cases:=[]struct{fb bool;k,b int;want float64}{{false,3,0,192},{false,3,1,193+1.0/3},{false,5,1,192.8},{true,3,0,192},{true,3,1,193+1.0/3},{true,5,1,192.8}}
 for _,c:=range cases{r:=synthStructured2(c.k,c.b,c.fb);if r.Count!=4096||!approx33(r.Worst,c.want){t.Fatalf("%+v want %.6f",r,c.want)}}
}
