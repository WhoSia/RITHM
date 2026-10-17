package main
import("encoding/json";"fmt";"os";"sort")
type Record struct{ID int `json:"id"`;Published int `json:"published"`;Received int `json:"received"`;Trusted bool `json:"trusted"`}
type Child struct{Observation [][]int `json:"observation"`;Key string `json:"key"`}
type Node struct{Action []int `json:"action"`;Children []Child `json:"children"`}
type Doc struct{Schema string `json:"schema"`;H int `json:"horizon"`;Budget int `json:"boost_budget"`;Records []Record `json:"records"`;Root string `json:"root"`;Nodes map[string]Node `json:"nodes"`}
type State [3]int
func encode(v any)string{b,_:=json.Marshal(v);return string(b)}
func worlds(h int)[][]int{w:=make([][]int,h+1);for i:=range w{w[i]=make([]int,h);if i>0{w[i][i-1]=1}};return w}
func observe(rs []Record,t int,w []int)[][]int{out:=[][]int{};seen:=map[int]bool{};for _,r:=range rs{if r.Trusted&&r.Received==t&&r.Published<=t&&!seen[r.ID]{out=append(out,[]int{r.ID,w[r.ID]});seen[r.ID]=true}};sort.Slice(out,func(i,j int)bool{return out[i][0]<out[j][0]});return out}
func key(t int,s []State,last,trained,spent int)string{return encode([]any{t,s,last,trained,spent})}
func bit(x bool)int{if x{return 1};return 0}
func verify(d Doc)error{
 if d.Schema!="rithm.p1p9.policy.v1"||d.H<1||d.H>12||d.Budget<0||d.Budget>d.H{return fmt.Errorf("schema")}
 if len(d.Records)!=d.H{return fmt.Errorf("records count")}
 ids:=map[int]bool{};for _,r:=range d.Records{if r.ID<0||r.ID>=d.H||ids[r.ID]||r.Published<r.ID+1||r.Received<r.Published{return fmt.Errorf("source time or event id")};ids[r.ID]=true}
 w:=worlds(d.H);first:=make([]State,len(w));for i:=range first{first[i]=State{i,0,0}}
 if d.Root!=key(0,first,2,0,0){return fmt.Errorf("wrong root")}
 visited:=map[string]bool{};var walk func(int,[]State,int,int,int)error
 walk=func(t int,states []State,last,trained,spent int)error{
  if t==d.H{for _,s:=range states{if s[1]!=2||s[2]!=2{return fmt.Errorf("unfinished recipient")}};return nil}
  k:=key(t,states,last,trained,spent);node,ok:=d.Nodes[k];if !ok{return fmt.Errorf("missing node")};visited[k]=true
  if len(node.Action)!=2{return fmt.Errorf("action shape")}
  who,boost:=node.Action[0],node.Action[1];if who<0||who>1||boost<0||boost>1||spent+boost>d.Budget{return fmt.Errorf("budget or action")}
  sw:=last!=2&&last!=who;groups:=map[string][]State{}
  for _,s:=range states{cap:=1+boost-w[s[0]][t]-bit(sw&&trained==0);if cap<0{cap=0};next:=s
   if who==0{next[1]+=cap;if next[1]>2{next[1]=2}}else{next[2]+=cap;if next[2]>2{next[2]=2}}
   o:=encode(observe(d.Records,t+1,w[s[0]]));groups[o]=append(groups[o],next)
  }
  if len(groups)!=len(node.Children){return fmt.Errorf("observation branches")}
  branches:=map[string]string{};for _,c:=range node.Children{o:=encode(c.Observation);if _,ok:=groups[o];!ok{return fmt.Errorf("invented observation")};if _,ok:=branches[o];ok{return fmt.Errorf("duplicate branch")};branches[o]=c.Key}
  for o,g:=range groups{want:=key(t+1,g,who,trained|bit(sw),spent+boost);if branches[o]!=want{return fmt.Errorf("branch key mismatch")};if err:=walk(t+1,g,who,trained|bit(sw),spent+boost);err!=nil{return err}}
  return nil
 }
 if err:=walk(0,first,2,0,0);err!=nil{return err};if len(visited)!=len(d.Nodes){return fmt.Errorf("unreachable excess nodes")};return nil
}
func main(){if len(os.Args)!=2{panic("pass JSON policy path")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var doc Doc;if e=json.Unmarshal(b,&doc);e!=nil{panic(e)};if e=verify(doc);e!=nil{fmt.Fprintln(os.Stderr,"FAIL",e);os.Exit(1)};fmt.Println("PASS independent Go policy verification",len(doc.Nodes),"nodes")}
