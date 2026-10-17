package main
import "fmt"
type Key struct{T,A,B,Prev,Used,Trained int}
func bit(x bool)int{if x{return 1};return 0}
func check(mode,goal string,h int)int{
 memo:=map[Key]int{}
 var solve func(Key)int
 solve=func(s Key)int{
  if s.T==h{switch goal{case "count":return bit(s.A==2)+bit(s.B==2);case "a":return bit(s.A==2);case "b":return bit(s.B==2);case "both":return bit(s.A==2&&s.B==2);case "weighted":return bit(s.A==2)+3*bit(s.B==2)}}
  if v,ok:=memo[s];ok{return v}
  best:=-1
  for action:=0;action<2;action++{worst:=100
   for w:=0;w<2;w++{if w==1&&s.Used==1{continue}
    n:=s;n.T++;n.Used|=w;n.Prev=action
    sw:=s.Prev!=2&&s.Prev!=action
    lost:=(mode=="always"&&sw)||(mode=="learn_once"&&sw&&s.Trained==0)
    if sw{n.Trained=1}
    if w==0&&!lost{if action==0&&n.A<2{n.A++};if action==1&&n.B<2{n.B++}}
    if v:=solve(n);v<worst{worst=v}
   };if worst>best{best=worst}
  };memo[s]=best;return best
 }
 return solve(Key{Prev:2})
}
func main(){goals:=[]string{"count","a","b","both","weighted"}
 expected:=map[string][]int{"none":{2,1,1,1,4},"learn_once":{1,1,1,0,3},"always":{1,1,1,0,3}}
 for _,mode:=range []string{"none","learn_once","always"}{for i,g:=range goals{v:=check(mode,g,5);if v!=expected[mode][i]{panic("crosscheck failure")};fmt.Printf("PASS %s %s %d\n",mode,g,v)}}
 if check("learn_once","both",6)!=1{panic("H6 threshold failed")}
}