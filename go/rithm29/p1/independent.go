package main
import("encoding/json";"fmt";"math/big")
type Rat=*big.Rat
func rt(a,b int64)Rat{return big.NewRat(a,b)}
func plus(a,b Rat)Rat{return new(big.Rat).Add(a,b)}
func half(a Rat)Rat{return new(big.Rat).Quo(a,rt(2,1))}
func quarter(a Rat)Rat{return new(big.Rat).Quo(a,rt(4,1))}
type Entry struct{I,J int;Costs [2]Rat}
type Stage struct{Previous [2]int; Remaining int; Chosen [2]int;Equilibria int; Costs [2]string}
func main(){
 values:=make([][4][2]Rat,4)
 for n:=0;n<4;n++{for i:=0;i<4;i++{values[n][i]=[2]Rat{rt(0,1),rt(0,1)}}}
 stages:=[]Stage{}
 for t:=1;t<=3;t++{for prev:=0;prev<4;prev++{
  entries:=[]Entry{}
  for a:=0;a<2;a++{for b:=0;b<2;b++{
    pay:=[2]Rat{rt(0,1),rt(0,1)}
    for x:=0;x<2;x++{for y:=0;y<2;y++{
       parity:=x^y;r0:=0;r1:=0;if a==1{r0=parity};if b==1{r1=parity}
       routes:=[2]int{r0,r1}
       for i,r:=range routes{
         load:=1;if r==routes[1-i]{load=2}
         cost:=rt(int64(load),1)
         if r!=parity{cost=plus(cost,rt(2,1))}
         if (i==0&&a==1)||(i==1&&b==1){cost=plus(cost,rt(1,1))}
         prevbit:=(prev>>uint(1-i))&1
         if r!=prevbit{cost=plus(cost,rt(1,2))}
         next:=2*r0+r1
         cost=plus(cost,values[t-1][next][i])
         pay[i]=plus(pay[i],quarter(cost))
       }
    }}
    entries=append(entries,Entry{a,b,pay})
  }}
  eq:=[]Entry{}
  for _,row:=range entries{
    valid:=true
    for _,other:=range entries{
     if other.J==row.J&&other.Costs[0].Cmp(row.Costs[0])<0{valid=false}
     if other.I==row.I&&other.Costs[1].Cmp(row.Costs[1])<0{valid=false}
    }
    if valid{eq=append(eq,row)}
  }
  if len(eq)==0{panic("no pure equilibrium")}
  selected:=eq[0]
  for _,e:=range eq[1:]{
    c1:=plus(e.Costs[0],e.Costs[1]);c2:=plus(selected.Costs[0],selected.Costs[1])
    if c1.Cmp(c2)<0||(c1.Cmp(c2)==0&&(e.I<selected.I||(e.I==selected.I&&e.J<selected.J))){selected=e}
  }
  values[t][prev]=selected.Costs
  stages=append(stages,Stage{[2]int{prev/2,prev%2},t,[2]int{selected.I,selected.J},len(eq),[2]string{selected.Costs[0].RatString(),selected.Costs[1].RatString()}})
 }}
 out:=struct{Horizon int;Initial []string;States []Stage}{3,
 []string{values[3][0][0].RatString(),values[3][0][1].RatString()},stages}
 b,_:=json.Marshal(out);fmt.Println(string(b))
}
