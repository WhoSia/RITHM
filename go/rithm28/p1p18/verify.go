package main

// Independent, synthetic-only verifier for exact winning/losing certificates.
// It never calls Ruby policy synthesis and never claims real beneficiary welfare.
import (
 "bytes"
 "encoding/json"
 "fmt"
 "io"
 "os"
 "sort"
)
const schema="rithm.p1p18.revocation_game.v1"
type Config struct {
 H int `json:"horizon"`
 Budget int `json:"budget"`
 ProbeCost int `json:"probe_cost"`
 Delay int `json:"delay"`
 Revoke int `json:"revoke_at"`
 Restore int `json:"restore_at"`
}
type Child struct {Observation int `json:"observation"`;Key string `json:"key"`}
type Counterexample struct {Action []int `json:"action"`;Observation int `json:"observation"`;Key string `json:"key"`}
type Node struct {
 Action []int `json:"action"`
 Children []Child `json:"children"`
 Counterexamples []Counterexample `json:"counterexamples"`
}
type Doc struct {
 Schema string `json:"schema"`
 Config Config `json:"config"`
 Type string `json:"certificate_type"`
 Root string `json:"root"`
 Nodes map[string]Node `json:"nodes"`
 Synthetic bool `json:"synthetic_only"`
 RealWelfare bool `json:"real_world_welfare_verified"`
}
type Row [3]int
type State struct{ T int; Rows []Row;Last,Setup,Spent int;Probes []int }
type Outcome struct{O int;S State}
func encode(v any)string{b,_:=json.Marshal(v);return string(b)}
func key(s State)string{return encode([]any{s.T,s.Rows,s.Last,s.Setup,s.Spent,s.Probes})}
func root(h int)State{rows:=make([]Row,h+1);for i:=range rows{rows[i]=Row{i,0,0}};return State{Rows:rows,Last:2,Probes:[]int{}}}
func legal(c Config,s State)[][]int{
 out:=[][]int{}
 for person:=0;person<2;person++{for boost:=0;boost<2;boost++{for probe:=0;probe<2;probe++{
  if s.Spent+boost+probe*c.ProbeCost<=c.Budget{out=append(out,[]int{person,boost,probe})}
 }}}
 return out
}
func equal(a,b []int)bool{if len(a)!=len(b){return false};for i:=range a{if a[i]!=b[i]{return false}};return true}
func max(x,y int)int{if x>y{return x};return y}
func min(x,y int)int{if x<y{return x};return y}
func includes(xs []int,n int)bool{for _,x:=range xs{if x==n{return true}};return false}
func outcomes(c Config,s State,a []int)[]Outcome{
 person,boost,probe:=a[0],a[1],a[2]
 switching:=s.Last!=2&&s.Last!=person
 setup:=s.Setup
 if switching{setup=1}
 probes:=append([]int{},s.Probes...)
 if probe==1{probes=append(probes,s.T)}
 event:=s.T+1-c.Delay
 trusted:=s.T+1<c.Revoke||s.T+1>=c.Restore
 usable:=event>=0&&includes(probes,event)&&trusted
 grouped:=map[int][]Row{}
 for _,row:=range s.Rows{
  outage:=0;if row[0]==s.T+1{outage=1}
  setupLoss:=0;if switching&&s.Setup==0{setupLoss=1}
  capacity:=max(0,1+boost-outage-setupLoss)
  next:=row
  if person==0{next[1]=min(2,row[1]+capacity)}else{next[2]=min(2,row[2]+capacity)}
  obs:=2
  if usable{obs=0;if row[0]==event+1{obs=1}}
  grouped[obs]=append(grouped[obs],next)
 }
 labels:=[]int{};for obs:=range grouped{labels=append(labels,obs)};sort.Ints(labels)
 result:=[]Outcome{}
 for _,obs:=range labels{
  result=append(result,Outcome{O:obs,S:State{T:s.T+1,Rows:grouped[obs],Last:person,Setup:setup,Spent:s.Spent+boost+probe*c.ProbeCost,Probes:probes}})
 }
 return result
}
func terminalWin(s State)bool{
 for _,r:=range s.Rows{if r[1]!=2||r[2]!=2{return false}}
 return true
}
func checkConfig(c Config)error{
 if c.H<1||c.H>7||c.Budget<0||c.Budget>4||c.ProbeCost<0||c.ProbeCost>2||
  c.Delay<1||c.Delay>c.H||c.Revoke<0||c.Revoke>c.H+1||
  c.Restore<c.Revoke||c.Restore>c.H+1{return fmt.Errorf("invalid config")}
 return nil
}
func verify(d Doc)error{
 if d.Schema!=schema||!d.Synthetic||d.RealWelfare||(d.Type!="winning"&&d.Type!="losing"){return fmt.Errorf("claim metadata")}
 if err:=checkConfig(d.Config);err!=nil{return err}
 first:=root(d.Config.H);if d.Root!=key(first){return fmt.Errorf("wrong root")}
 if len(d.Nodes)>30000{return fmt.Errorf("oversize certificate")}
 visited:=map[string]bool{}
 var walk func(State)error
 walk=func(s State)error{
  if s.T==d.Config.H{
   win:=terminalWin(s)
   if d.Type=="winning"&&!win{return fmt.Errorf("unfinished recipient")}
   if d.Type=="losing"&&win{return fmt.Errorf("falsely losing terminal")}
   return nil
  }
  k:=key(s);node,ok:=d.Nodes[k];if !ok{return fmt.Errorf("missing node at %d",s.T)}
  if visited[k]{return nil};visited[k]=true
  acts:=legal(d.Config,s)
  if d.Type=="winning"{
   if len(node.Action)!=3||len(node.Counterexamples)!=0{return fmt.Errorf("winning node shape")}
   valid:=false
   for _,a:=range acts{if equal(a,node.Action){valid=true;break}}
   if !valid{return fmt.Errorf("budget or action")}
   possible:=outcomes(d.Config,s,node.Action)
   if len(node.Children)!=len(possible){return fmt.Errorf("missing observation branch")}
   for _,out:=range possible{
    count:=0
    for _,child:=range node.Children{
     if child.Observation==out.O{count++;if child.Key!=key(out.S){return fmt.Errorf("bad child state")}}
    }
    if count!=1{return fmt.Errorf("duplicate/missing branch")}
    if err:=walk(out.S);err!=nil{return err}
   }
  }else{
   if len(node.Action)!=0||len(node.Children)!=0||len(node.Counterexamples)!=len(acts){return fmt.Errorf("incomplete action counterexamples")}
   used:=make([]bool,len(acts))
   for _,ce:=range node.Counterexamples{
    idx:=-1;for i,a:=range acts{if equal(a,ce.Action){idx=i;break}}
    if idx<0||used[idx]{return fmt.Errorf("illegal/repeated counteraction")};used[idx]=true
    valid:=false
    for _,out:=range outcomes(d.Config,s,ce.Action){
     if ce.Observation==out.O&&ce.Key==key(out.S){
      valid=true
      if err:=walk(out.S);err!=nil{return err}
      break
     }
    }
    if !valid{return fmt.Errorf("fabricated counterexample branch")}
   }
  }
  return nil
 }
 if err:=walk(first);err!=nil{return err}
 if len(visited)!=len(d.Nodes){return fmt.Errorf("unreachable excess node")}
 return nil
}
// Reject duplicate object keys prior to Go JSON's otherwise last-key-wins decoding.
func noDuplicateKeys(data []byte)error{
 d:=json.NewDecoder(bytes.NewReader(data))
 var walk func()error
 walk=func()error{
  tok,e:=d.Token();if e!=nil{return e}
  delim,ok:=tok.(json.Delim);if !ok{return nil}
  switch delim{
  case '{':
   seen:=map[string]bool{}
   for d.More(){
    k,e:=d.Token();if e!=nil{return e}
    name,ok:=k.(string);if !ok{return fmt.Errorf("object key")}
    if seen[name]{return fmt.Errorf("duplicate key")}
    seen[name]=true
    if e=walk();e!=nil{return e}
   }
   _,e:=d.Token();return e
  case '[':
   for d.More(){if e:=walk();e!=nil{return e}}
   _,e:=d.Token();return e
  default:return fmt.Errorf("unexpected JSON token")
  }
 }
 if e:=walk();e!=nil{return e}
 if _,e:=d.Token();e!=io.EOF{return fmt.Errorf("trailing JSON")}
 return nil
}
func main(){
 if len(os.Args)!=2{fmt.Fprintln(os.Stderr,"usage: verify CERT.json");os.Exit(2)}
 b,err:=os.ReadFile(os.Args[1]);if err!=nil{panic(err)}
 if len(b)>20_000_000{fmt.Fprintln(os.Stderr,"FAIL too large");os.Exit(1)}
 if err=noDuplicateKeys(b);err!=nil{fmt.Fprintln(os.Stderr,"FAIL",err);os.Exit(1)}
 var d Doc
 decoder:=json.NewDecoder(bytes.NewReader(b));decoder.DisallowUnknownFields()
 if err=decoder.Decode(&d);err!=nil{fmt.Fprintln(os.Stderr,"FAIL",err);os.Exit(1)}
 if err=verify(d);err!=nil{fmt.Fprintln(os.Stderr,"FAIL",err);os.Exit(1)}
 fmt.Printf("PASS independent Go %s certificate (%d nodes)
",d.Type,len(d.Nodes))
}
