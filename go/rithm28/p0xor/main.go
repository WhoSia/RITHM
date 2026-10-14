package main
import("fmt";"math/bits")
func legal(w uint64,k,b int)bool{for t:=0;t+k<=12;t++{if bits.OnesCount64((w>>t)&uint64((1<<k)-1))>b{return false}};return true}
func replay(fb bool,w uint64,z int)bool{prev,mem,last:=z,z,0;for t:=0;t<12;t++{a:=1-prev;if fb{a=mem};d:=a^z;if t>0&&d!=last{return false};shock:=int((w>>t)&1);next:=z^1^shock;if fb{next^=d};prev=z;z=next;mem^=1;last=shock};return true}
func main(){count:=0;for _,f:=range []bool{false,true}{for _,k:=range []int{3,5}{for b:=0;b<=k;b++{for z:=0;z<2;z++{for w:=uint64(0);w<1<<12;w++{if legal(w,k,b){if !replay(f,w,z){panic("witness identity")};count++}}};fmt.Printf("fb=%v K=%d B=%d V=%.9f\n",f,k,b,192+4*float64(b)/float64(k))}}};if count!=63972{panic("count mismatch")};fmt.Printf("witness histories=%d\n",count)}
