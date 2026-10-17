package main
import (
 "crypto/sha256"
 "encoding/json"
 "fmt"
 "sort"
)
type Record struct{ID,Published,Received int;Trusted bool}
func evidence(h,lag,pub int)[]Record{out:=[]Record{};for i:=0;i<h;i++{out=append(out,Record{i,i+pub,i+lag,true})};return out}
func worlds(h int)[][]int{out:=[][]int{};for i:=0;i<=h;i++{w:=make([]int,h);if i>0{w[i-1]=1};out=append(out,w)};return out}
func observe(rs []Record,t int,w []int)string{p:=[][2]int{};for _,r:=range rs{if r.Trusted&&r.Received==t{p=append(p,[2]int{r.ID,w[r.ID]})}};sort.Slice(p,func(i,j int)bool{return p[i][0]<p[j][0]});b,_:=json.Marshal(p);return string(b)}
func equivalent(a,b []Record,h int)bool{for _,w:=range worlds(h){for t:=0;t<=h;t++{if observe(a,t,w)!=observe(b,t,w){return false}}};return true}
func hash(rs []Record)[32]byte{b,_:=json.Marshal(rs);return sha256.Sum256(b)}
func main(){h:=5;a:=evidence(h,4,1);b:=evidence(h,4,2);c:=evidence(h,4,1);c[0].Received=3
 if !equivalent(a,b,h)||hash(a)==hash(b)||equivalent(a,c,h){panic("P1-P10 oracle mismatch")}
 fmt.Printf("PASS Go: %d worlds; observational identity differs from provenance identity\n",len(worlds(h)))
}