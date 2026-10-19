package main

import (
 "encoding/json"
 "fmt"
 "os"
 "strconv"
)
func vector(n, mask int) []int {
 v:=make([]int,n)
 for i:=0;i<n;i++ {v[i]=(mask>>(n-i-1))&1}
 return v
}
func hamming(a,b []int) int {
 n:=0
 for i:=range a {if a[i]!=b[i] {n++}}
 return n
}
func cost(v []int) int {
 a:=0
 for _,x:=range v {if x==0 {a++}}
 b:=len(v)-a
 return a*a+b*b
}
func abs(x int) int {if x<0{return -x};return x}
func main() {
 n:=3
 if len(os.Args)>1 {var err error;n,err=strconv.Atoi(os.Args[1]);if err!=nil {panic(err)}}
 if n<2||n>5 {panic("bounded cohort")}
 total,reverse,ties:=0,0,0
 var witness map[string]any
 lim:=1<<n
 for y:=0;y<lim;y++ {
  truth:=vector(n,y);yc:=cost(truth)
  for i:=0;i<lim;i++ {
   a:=vector(n,i);ha:=hamming(truth,a);ea:=abs(yc-cost(a))
   for j:=0;j<lim;j++ {
    b:=vector(n,j);hb:=hamming(truth,b)
    if ha>=hb {continue}
    total++
    eb:=abs(yc-cost(b))
    if ea==eb {ties++}
    if ea>eb {
     reverse++
     if witness==nil {witness=map[string]any{
      "truth":truth,"individual_better":a,"individual_worse":b,
      "better_hamming":ha,"worse_hamming":hb,"truth_cost":yc,
      "better_cost":cost(a),"worse_cost":cost(b),
      "better_cost_error":ea,"worse_cost_error":eb,"cost_rank_reversed":true}}
    }
   }
  }
 }
 out:=map[string]any{"cohort":n,"compared_strict_pairs":total,"rank_reversals":reverse,
 "tied_cost_errors":ties,"first_witness":witness,
 "source":"synthetic exhaustive binary assignments","causal_effect_identified":false}
 encoded,err:=json.MarshalIndent(out,"","  ");if err!=nil {panic(err)}
 fmt.Println(string(encoded))
}
