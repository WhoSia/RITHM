package main
import("fmt";"math/bits")
func labelSwap(x int)int{if x==2{return 3};if x==3{return 2};return x}
func action(a,m,o int)int{return(a>>(2*m+o))&1}
func update(u,m,o int)int{return(u>>(2*(2*m+o)))&3}
func conjugateAction(a int)int{v:=0;for m:=0;m<4;m++{for o:=0;o<2;o++{v|=action(a,labelSwap(m),o)<<(2*m+o)}};return v}
func conjugateUpdate(u int)int{v:=0;for m:=0;m<4;m++{for o:=0;o<2;o++{v|=labelSwap(update(u,labelSwap(m),o))<<(2*(2*m+o))}};return v}
func closure(u int)int{r:=3;for{n:=r;for m:=0;m<4;m++{if r&(1<<m)==0{continue};for o:=0;o<2;o++{n|=1<<update(u,m,o)}};if n==r{return bits.OnesCount(uint(r))};r=n}}
func main(){dist:=[5]int{};fixedU:=0;for u:=0;u<65536;u++{dist[closure(u)]++;if conjugateUpdate(u)==u{fixedU++}};fixedA:=0;for a:=0;a<256;a++{if conjugateAction(a)==a{fixedA++}}
 orbits:=(16777216+fixedA*fixedU)/2
 if fixedA!=64||fixedU!=256||orbits!=8396800||dist[2]!=4096||dist[3]!=18720||dist[4]!=42720{panic("P0 state quotient mismatch")}
 fmt.Printf("P0 symmetries: policies=%d orbits=%d closure2=%d closure3=%d closure4=%d\n",16777216,orbits,dist[2],dist[3],dist[4])
}