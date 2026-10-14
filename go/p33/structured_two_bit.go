package main
import "math"
// Structured subset, NOT the 16,777,216 full 2-bit table-pair space.
// Mealy action depends on (two-bit memory, one-round delayed bit):
// 256 action maps. Memory update is a shift register with one new bit
// depending on previous low bit and delayed observation: 16 maps.
type Structured33 struct{K,B,Count int;Feedback,Safe bool;Worst float64;Act,Update int}
func synthStructured2(k,b int,feedback bool)Structured33{
 out:=Structured33{K:k,B:b,Feedback:feedback,Worst:math.Inf(1)}
 for act:=0;act<256;act++{for up:=0;up<16;up++{
  a,u:=act,up
  p:=Policy33{Name:"structured2",Bits:2,
   Act:func(s S33)int{return (a>>(2*s.Mem+s.Prev))&1},
   Upd:func(s S33)int{return ((s.Mem&1)<<1)|((u>>(2*(s.Mem&1)+s.Prev))&1)}}
  v,s,_:=solve33(p,k,b,false,feedback);out.Count++
  if v<out.Worst-1e-9||(math.Abs(v-out.Worst)<1e-9&&s&&!out.Safe){out.Worst=v;out.Safe=s;out.Act=a;out.Update=u}
 }}
 return out
}
