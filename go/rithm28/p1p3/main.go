package main
import "fmt"
type K struct{T,A,B,Prev,Used,TA,TB int}
func b(x bool)int{if x{return 1};return 0}
func solve(setup bool,obj string)(int,int){
 memo:=map[K]int{}
 var rec func(K)int
 rec=func(k K)int{
  if k.T==5{switch obj{
   case "count":return b(k.A==2)+b(k.B==2)
   case "deadline":return b(k.TA>0&&k.TA<=3)+b(k.TB>0&&k.TB<=3)
   case "weighted":return b(k.A==2)+3*b(k.B==2)
   case "min_group":return b(k.A==2&&k.B==2)
  }}
  if x,ok:=memo[k];ok{return x};best:=-1
  for act:=0;act<2;act++{worst:=999
   for shock:=0;shock<=1;shock++{if shock==1&&k.Used==1{continue}
    n:=k;n.T++;n.Prev=act;n.Used|=shock
    if shock==0&&(!setup||k.Prev==2||k.Prev==act){
     if act==0&&n.A<2{n.A++};if act==1&&n.B<2{n.B++}
    }
    if n.A==2&&n.TA==0{n.TA=k.T+1};if n.B==2&&n.TB==0{n.TB=k.T+1}
    if v:=rec(n);v<worst{worst=v}
   };if worst>best{best=worst}
  };memo[k]=best;return best
 };return rec(K{Prev:2}),len(memo)
}
func main(){for _,s:=range []bool{false,true}{for _,o:=range []string{"count","deadline","weighted","min_group"}{v,n:=solve(s,o);fmt.Printf("setup=%v objective=%s guaranteed=%d states=%d\n",s,o,v,n)}}}
