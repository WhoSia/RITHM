package main
import("encoding/json";"fmt";"math/big")
type R=*big.Rat
func rat(a,b int64)R{return big.NewRat(a,b)}
func add(a,b R)R{return new(big.Rat).Add(a,b)}
func key(x,y int)int{return x*2+y}
type V [4][2]R
func eq(f V,px,py int)[][2]R{
 rows:=[9][2]R{}
 for p:=0;p<3;p++{for q:=0;q<3;q++{
  c:=[2]R{rat(0,1),rat(0,1)}
  for z:=0;z<2;z++{
   a:=p;if p==2{a=z};b:=q;if q==2{b=z}
   for i:=0;i<2;i++{
    action:=a;other:=b;prev:=px;prog:=p;if i==1{action=b;other=a;prev=py;prog=q}
    load:=1;if action==other{load=2}
    val:=rat(int64(load),1)
    if action!=z{val=add(val,rat(2,1))}
    if prog==2{val=add(val,rat(1,1))}
    if action!=prev{val=add(val,rat(1,2))}
    val=add(val,f[key(a,b)][i])
    c[i]=add(c[i],new(big.Rat).Quo(val,rat(2,1)))
   }
  }
  rows[3*p+q]=c
 }}
 out:=[][2]R{}
 for p:=0;p<3;p++{for q:=0;q<3;q++{
  candidate:=rows[3*p+q];ok:=true
  for alt:=0;alt<3;alt++{
   if rows[3*alt+q][0].Cmp(candidate[0])<0||rows[3*p+alt][1].Cmp(candidate[1])<0{ok=false}
  }
  if ok{out=append(out,candidate)}
 }}
 return out
}
type Branch struct{Future V}
func main(){
 zero:=V{};for j:=0;j<4;j++{for i:=0;i<2;i++{zero[j][i]=rat(0,1)}}
 branches:=[]Branch{{zero}}
 counts:=[]int{}
 for t:=1;t<=3;t++{
  next:=[]Branch{}
  for _,br:=range branches{
   sets:=[4][][2]R{}
   possible:=true
   for s:=0;s<4;s++{sets[s]=eq(br.Future,s/2,s%2);if len(sets[s])==0{possible=false}}
   if !possible{continue}
   for _,a:=range sets[0]{for _,b:=range sets[1]{for _,c:=range sets[2]{for _,d:=range sets[3]{
    next=append(next,Branch{V{a,b,c,d}})
   }}}}
  }
  branches=next;counts=append(counts,len(branches))
 }
 welfare:=map[string]bool{}
 for _,br:=range branches{welfare[add(br.Future[0][0],br.Future[0][1]).RatString()]=true}
 out:=struct{Counts []int `json:"counts"`;Welfare map[string]bool `json:"welfare"`}{counts,welfare}
 b,_:=json.Marshal(out);fmt.Println(string(b))
}
