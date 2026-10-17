package main
import("crypto/hmac";"crypto/sha256";"encoding/hex";"encoding/json";"errors";"fmt";"os";"strconv";"strings")
type Event struct{Domain string `json:"domain"`;Issuer string `json:"issuer"`;Person string `json:"person"`;Episode string `json:"episode"`;EventID string `json:"event_id"`;Occurred int `json:"occurred"`;Published int `json:"published"`;Received int `json:"received"`;Outcome string `json:"outcome"`;KeyID string `json:"key_id"`;Mac string `json:"mac"`}
type Doc struct{Schema string `json:"schema"`;Synthetic bool `json:"synthetic"`;Evidence []Event `json:"evidence"`}
var keys=map[string]string{"receipt-test-v1":"synthetic-receipt-only-key","delivery-test-v1":"synthetic-delivery-only-key"}
func literal(v any)string{b,_:=json.Marshal(v);return string(b)}
func canonical(e Event)string{return strings.Join([]string{literal(e.Domain),literal(e.Issuer),literal(e.Person),literal(e.Episode),literal(e.EventID),strconv.Itoa(e.Occurred),strconv.Itoa(e.Published),strconv.Itoa(e.Received),literal(e.Outcome)},"|")}
func verify(d Doc)(bool,error){
 if d.Schema!="rithm.p1p11.typed-evidence.v1"||!d.Synthetic{return false,errors.New("not explicitly synthetic test fixture")}
 if len(d.Evidence)<1{return false,errors.New("empty evidence")}
 seen:=map[string]bool{};delivery:=false;subject:=""
 for _,e:=range d.Evidence{
  if e.Issuer!="constructed-institution"||e.Person==""||e.Episode==""||e.EventID==""||e.Occurred<0||e.Published<e.Occurred||e.Received<e.Published{return false,errors.New("bad identities or clocks")}
  identity:=e.Person+"/"+e.Episode;if subject==""{subject=identity}else if subject!=identity{return false,errors.New("cross-person episode collision")}
  id:=e.Issuer+"/"+e.EventID;if seen[id]{return false,errors.New("replay event ID")};seen[id]=true
  key,ok:=keys[e.KeyID];if !ok{return false,errors.New("untrusted test key")}
  if e.Domain=="client_receipt"&&e.KeyID!="receipt-test-v1"{return false,errors.New("receipt role mismatch")}
  if e.Domain=="benefit_delivery"&&e.KeyID!="delivery-test-v1"{return false,errors.New("delivery role mismatch")}
  if e.Domain!="client_receipt"&&e.Domain!="benefit_delivery"{return false,errors.New("unknown domain")}
  mac:=hmac.New(sha256.New,[]byte(key));mac.Write([]byte(canonical(e)))
  decoded,err:=hex.DecodeString(e.Mac);if err!=nil||!hmac.Equal(mac.Sum(nil),decoded){return false,errors.New("MAC failure")}
  if e.Domain=="benefit_delivery"&&e.Outcome=="benefit_delivered"{delivery=true}
 }
 return delivery,nil
}
func main(){if len(os.Args)!=2{panic("give JSON evidence path")};b,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var d Doc;if e=json.Unmarshal(b,&d);e!=nil{panic(e)};delivery,e:=verify(d);if e!=nil{fmt.Fprintln(os.Stderr,"REJECT",e);os.Exit(1)};fmt.Printf("ACCEPT synthetic MACs; synthetic_delivery_event=%v; real_world_benefit_certified=false\n",delivery)}
