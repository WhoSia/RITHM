package main
type Machine struct{ Act, Next, Init int }
func bit(x,k int)int{return(x>>k)&1}
func value(m Machine,z0 int)(float64,bool){
 z:=z0;mem:=bit(m.Init,z0); seen:=map[[2]int]int{}; costs:=[]int{}
 for{
  k:=[2]int{z,mem}
  if i,ok:=seen[k];ok{
   sum:=0;for _,c:=range costs[i:]{sum+=c}
   return float64(sum)/float64(len(costs)-i), allSafe(costs)
  }
  seen[k]=len(costs)
  a:=bit(m.Act,mem);d:=a-z;costs=append(costs,192+2*d*d)
  mem=bit(m.Next,mem);z=1-z
 }
}
func allSafe(c []int)bool{for _,v:=range c{if v>192{return false}};return true}
func enumerate()(int,int,int){
 total,opt,safe:=0,0,0
 for a:=0;a<4;a++{for n:=0;n<4;n++{for i:=0;i<4;i++{
  total++;m:=Machine{a,n,i}
  v0,s0:=value(m,0);v1,s1:=value(m,1)
  if v0==192&&v1==192{opt++};if s0&&s1{safe++}
 }}}
 return total,opt,safe
}
