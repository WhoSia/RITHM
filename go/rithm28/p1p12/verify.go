package main
import("bytes";"crypto/hmac";"crypto/sha256";"encoding/hex";"encoding/json";"errors";"fmt";"io";"os";"strconv";"strings")
type Event struct{Kind string `json:"kind"`;Issuer string `json:"issuer"`;Person string `json:"person"`;Episode string `json:"episode"`;ID string `json:"id"`;Parent string `json:"parent"`;Occurred int `json:"occurred"`;Published int `json:"published"`;Received int `json:"received"`;Result string `json:"result"`;Root string `json:"root"`;MAC string `json:"mac"`}
type Doc struct{Schema string `json:"schema"`;Synthetic bool `json:"synthetic"`;Records []Event `json:"records"`}
var roots=map[string]string{"client-log-test-root":"synthetic-client-log-secret","provider-test-root":"synthetic-provider-secret"}
func q(x string)string{v,_:=json.Marshal(x);return string(v)}
func canonical(e Event)string{return strings.Join([]string{q(e.Kind),q(e.Issuer),q(e.Person),q(e.Episode),q(e.ID),q(e.Parent),strconv.Itoa(e.Occurred),strconv.Itoa(e.Published),strconv.Itoa(e.Received),q(e.Result)},"|")}
func Verify(d Doc)(string,error){
 if d.Schema!="rithm.p1p12.two-roots.v1"||!d.Synthetic{return "",errors.New("schema or unverified real evidence")}
 if len(d.Records)<1||len(d.Records)>2{return "",errors.New("record count")}
 var receipt,delivery *Event
 seen:=map[string]bool{}
 for i:=range d.Records{
  e:= &d.Records[i]
  if e.ID==""||e.Person==""||e.Episode==""||e.Occurred<0||e.Published<e.Occurred||e.Received<e.Published||seen[e.ID]{return "",errors.New("invalid event/clock/id")}
  seen[e.ID]=true
  secret,ok:=roots[e.Root];if !ok{return "",errors.New("unrecognized test trust root")}
  h:=hmac.New(sha256.New,[]byte(secret));h.Write([]byte(canonical(*e)))
  given,err:=hex.DecodeString(e.MAC);if err!=nil||!hmac.Equal(h.Sum(nil),given){return "",errors.New("MAC invalid")}
  switch e.Kind{
  case "client_receipt":
   if receipt!=nil||e.Root!="client-log-test-root"||e.Issuer!="synthetic-client-log"||e.Parent!=""||e.Result!="received"{return "",errors.New("receipt type authority")};receipt=e
  case "benefit_delivery":
   if delivery!=nil||e.Root!="provider-test-root"||e.Issuer!="synthetic-provider"||e.Parent==""||e.Result!="delivered"{return "",errors.New("delivery type authority")};delivery=e
  default:return "",errors.New("unknown evidence kind")
  }
 }
 if receipt==nil{return "",errors.New("missing authenticated receipt")}
 if delivery==nil{return "receipt_only_unconfirmed",nil}
 if receipt.ID!=delivery.Parent||receipt.Person!=delivery.Person||receipt.Episode!=delivery.Episode||delivery.Occurred<receipt.Received{return "",errors.New("not same documented recovery chain")}
 return "synthetic_delivery_chain_only",nil
}
func main(){if len(os.Args)!=2{panic("usage: verify fixture.json")};data,e:=os.ReadFile(os.Args[1]);if e!=nil{panic(e)};var d Doc;dec:=json.NewDecoder(bytes.NewReader(data));dec.DisallowUnknownFields();if e=dec.Decode(&d);e!=nil{panic(e)};var other any;if e=dec.Decode(&other);e!=io.EOF{panic("extra JSON or decoding failure")};status,e:=Verify(d);if e!=nil{fmt.Fprintln(os.Stderr,"REJECT",e);os.Exit(1)};fmt.Printf("ACCEPT %s real_world_welfare_verified=false\n",status)}
