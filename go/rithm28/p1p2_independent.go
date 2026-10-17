package main
import "fmt"
func worst(r,d int,s string)int{switch s{case "off":return 1+worst(r,d,"on");case "on":v:=1+worst(r,d,"ordered");if r>0{if n:=1+worst(r-1,d,"off");n>v{v=n}};return v;case "ordered":if d>0{return 1+worst(r,d-1,"ordered")};return 1};panic(s)}
func main(){for _,v:=range [][3]int{{0,0,3},{1,0,5},{2,1,8},{3,2,11}}{n:=worst(v[0],v[1],"off");if n!=v[2]{panic("bound mismatch")};fmt.Printf("r=%d d=%d bound=%d PASS\n",v[0],v[1],n)}}
