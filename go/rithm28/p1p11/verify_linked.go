package main
import (
 "bytes"
 "crypto/hmac"
 "crypto/sha256"
 "encoding/hex"
 "encoding/json"
 "errors"
 "fmt"
 "os"
 "strconv"
 "strings"
)
type Event struct {
 Domain string `json:"domain"`
 Issuer string `json:"issuer"`
 Person string `json:"person"`
 Episode string `json:"episode"`
 EventID string `json:"event_id"`
 ParentEventID string `json:"parent_event_id"`
 Occurred int `json:"occurred"`
 Published int `json:"published"`
 Received int `json:"received"`
 Outcome string `json:"outcome"`
 KeyID string `json:"key_id"`
 MAC string `json:"mac"`
}
type Document struct {
 Schema string `json:"schema"`
 Synthetic bool `json:"synthetic"`
 Evidence []Event `json:"evidence"`
}
var keys=map[string]string{
 "receipt-test-v2":"synthetic-receipt-role-secret",
 "delivery-test-v2":"synthetic-delivery-role-secret",
}
func js(v string) string {b,_:=json.Marshal(v);return string(b)}
func canonical(e Event) string {
 return strings.Join([]string{
 js(e.Domain),js(e.Issuer),js(e.Person),js(e.Episode),js(e.EventID),
 js(e.ParentEventID),strconv.Itoa(e.Occurred),strconv.Itoa(e.Published),
 strconv.Itoa(e.Received),js(e.Outcome),
 },"|")
}
func Verify(d Document)(bool,error){
 if d.Schema!="rithm.p1p11.linked-evidence.v2"||!d.Synthetic{return false,errors.New("synthetic schema required")}
 if len(d.Evidence)<1||len(d.Evidence)>2{return false,errors.New("unexpected evidence cardinality")}
 events:=map[string]Event{}
 receiptCount,deliveryCount:=0,0
 for _,e:=range d.Evidence {
  if e.Issuer!="synthetic-agency"||e.Person==""||e.Episode==""||e.EventID==""||e.Occurred<0||e.Published<e.Occurred||e.Received<e.Published{return false,errors.New("bad identity or chronology")}
  if _,ok:=events[e.EventID];ok{return false,errors.New("replayed event id")}
  key,ok:=keys[e.KeyID];if !ok{return false,errors.New("untrusted key")}
  if e.Domain=="client_receipt" {
   if e.KeyID!="receipt-test-v2"||e.Outcome!="appeal_acknowledged"||e.ParentEventID!=""{return false,errors.New("invalid receipt role/parent/outcome")}
   receiptCount++
  }else if e.Domain=="benefit_delivery" {
   if e.KeyID!="delivery-test-v2"||e.Outcome!="benefit_delivered"||e.ParentEventID==""{return false,errors.New("invalid delivery role/parent/outcome")}
   deliveryCount++
  }else{return false,errors.New("unknown role")}
  mac:=hmac.New(sha256.New,[]byte(key));mac.Write([]byte(canonical(e)))
  got,err:=hex.DecodeString(e.MAC)
  if err!=nil||!hmac.Equal(got,mac.Sum(nil)){return false,errors.New("HMAC mismatch")}
  events[e.EventID]=e
 }
 if receiptCount!=1||deliveryCount>1{return false,errors.New("invalid cardinality")}
 if deliveryCount==0{return false,nil}
 var receipt,delivery Event
 for _,e:=range events {if e.Domain=="client_receipt"{receipt=e}else{delivery=e}}
 if delivery.ParentEventID!=receipt.EventID{return false,errors.New("wrong parent event")}
 if delivery.Issuer!=receipt.Issuer||delivery.Person!=receipt.Person||delivery.Episode!=receipt.Episode{return false,errors.New("cross-subject evidence binding")}
 if receipt.Received>delivery.Occurred{return false,errors.New("delivery predates receipt confirmation")}
 return true,nil
}
func main(){
 if len(os.Args)!=2{fmt.Fprintln(os.Stderr,"usage: verify_linked <fixture.json>");os.Exit(2)}
 data,err:=os.ReadFile(os.Args[1]);if err!=nil{panic(err)}
 var d Document
 dec:=json.NewDecoder(bytes.NewReader(data));dec.DisallowUnknownFields()
 if err=dec.Decode(&d);err!=nil{fmt.Fprintln(os.Stderr,"REJECT JSON",err);os.Exit(1)}
 var extra any;if err=dec.Decode(&extra);err==nil{fmt.Fprintln(os.Stderr,"REJECT trailing JSON");os.Exit(1)}
 ok,err:=Verify(d);if err!=nil{fmt.Fprintln(os.Stderr,"REJECT",err);os.Exit(1)}
 fmt.Printf("ACCEPT synthetic_linked_delivery=%v; real_world_benefit_certified=false\n",ok)
}