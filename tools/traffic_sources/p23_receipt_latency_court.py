#!/usr/bin/env python3
"""P23 synthetic receipt-admissibility falsifier (compact repo implementation).
All traffic values, receipt timestamps and attestation flags are SYNTHETIC.
For richer original-source overlay and 51 tests, see the P23 scientific packet.
"""
import argparse, hashlib, json
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from pathlib import Path
FIVE=timedelta(minutes=5);TEN=timedelta(minutes=10)
def utc(t):
    if not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timezone-aware clock needed")
    return t.astimezone(timezone.utc)
@dataclass(frozen=True)
class Observation:
    oid:str; link:str; direction:str; end:datetime; version:int; count:int
    def __post_init__(self):
        d=utc(self.end)
        if not self.oid or not self.link or not self.direction or type(self.version)!=int or self.version<1:
            raise ValueError("source identity and version required")
        if type(self.count)!=int or self.count<0 or d.minute%5 or d.second:
            raise ValueError("invalid five-minute source")
    @property
    def digest(self):
        return hashlib.sha256(repr((self.oid,self.link,self.direction,utc(self.end).isoformat(),self.version,self.count)).encode()).hexdigest()
@dataclass(frozen=True)
class Receipt:
    oid:str; version:int; received:datetime; digest:str
    origin:bool=True; attested:bool=True; cache:str="origin"
    def __post_init__(self):
        utc(self.received)
        if self.cache not in ("origin","stale","unverified"):raise ValueError("invalid cache")
@dataclass(frozen=True)
class Probe:
    oid:str; at:datetime; positive:bool
    origin:bool=True; uncached:bool=True; attested:bool=True
    def __post_init__(self):utc(self.at)
def publication_interval(observation,probes):
    ps=[p for p in probes if p.oid==observation.oid and p.origin and p.uncached and p.attested
        and utc(p.at)>=utc(observation.end)]
    lo=max((utc(p.at) for p in ps if not p.positive),default=utc(observation.end))
    hi=min((utc(p.at) for p in ps if p.positive),default=None)
    if hi is not None and hi<=lo:raise ValueError("contradictory origin polls")
    return lo,hi
def asof(source,receipts,t):
    decision=utc(t)
    byid={(s.oid,s.version):s for s in source}
    if len(byid)!=len(source):raise ValueError("duplicate source version")
    visible={}
    for r in receipts:
        s=byid.get((r.oid,r.version))
        if s is None or s.digest!=r.digest or utc(r.received)<utc(s.end):
            raise ValueError("missing, corrupted, prematurely received source")
        if not (r.attested and r.origin and r.cache=="origin" and utc(r.received)<=decision):
            continue
        key=(s.link,s.direction,utc(s.end))
        prev=visible.get(key)
        if prev is None or (s.version,utc(r.received))>(prev[0].version,utc(prev[1].received)):
            visible[key]=(s,r)
    return {key:item[0] for key,item in visible.items()}
def pair(source,receipts,decision,link,direction,at_end=None):
    allowed=asof(source,receipts,decision);possible=[]
    for (l,dr,end),b in allowed.items():
        if l!=link or dr!=direction or end.minute%10:continue
        if at_end is not None and utc(at_end)!=end:continue
        a=allowed.get((link,direction,end-FIVE))
        if a is not None and a.oid!=b.oid:possible.append((end,a.count+b.count))
    return max(possible,default=None)
def policy(source,receipts,t,calendar,choice):
    d=utc(t)
    if choice=="calendar":return float(calendar),"calendar"
    if choice=="lag7":
        # Predict Y_(k+1) from Y_(k-6) = lag7 of the target.
        lagend=d-timedelta(minutes=2)-TEN*6
        available=pair(source,receipts,d,"A","inbound",lagend)
    else:available=pair(source,receipts,d,"A","inbound")
    if available is None or (choice=="receipt" and d-available[0]>timedelta(minutes=30)):
        return float(calendar),"fallback"
    return float(available[1]),"received_pair"
def mean_bound(n,N,mean,B):
    if not (0<=n<=N and N>0 and 0<=mean<=B):raise ValueError("invalid bounds")
    q=n/N;return [q*mean,q*mean+(1-q)*B]
def world(label):
    if label not in ("fast","congestion_delayed","uniform_60"):raise ValueError("unknown world")
    start=datetime(2025,10,1,tzinfo=timezone.utc)
    src=[];receipts=[];counts=[];times=[]
    for k in range(60):
        end=start+TEN*(k+1);high=20<=k<40;volume=120 if high else 20
        for h in (0,1):
            o=Observation(f"A-{k}-{h}","A","inbound",end-FIVE if h==0 else end,1,volume//2)
            delay=60 if label=="uniform_60" else 22 if label=="congestion_delayed" and high else 1
            src.append(o);receipts.append(Receipt(o.oid,1,o.end+timedelta(minutes=delay),o.digest))
        counts.append(volume);times.append(end+timedelta(minutes=2))
    return src,receipts,counts,times
def evaluate(label):
    src,r,counts,times=world(label)
    scores={name:[] for name in ("calendar","receipt","lag7","unreceived_csv_ILLEGAL")}
    n=0;received=[];states={s:{"n":0,"received":0} for s in ("normal","congested")}
    for k in range(7,59):
        decision=times[k];target=counts[k+1];state="congested" if counts[k]==120 else "normal"
        latest=pair(src,r,decision,"A","inbound")
        available=bool(latest and latest[0]==src[2*k+1].end)
        states[state]["n"]+=1;states[state]["received"]+=int(available)
        predictions={name:policy(src,r,decision,40,name)[0] for name in ("calendar","receipt","lag7")}
        predictions["unreceived_csv_ILLEGAL"]=counts[k]
        for name,pred in predictions.items():scores[name].append(abs(pred-target))
        if available:received.append(abs(predictions["receipt"]-target))
        n+=1
    means={name:sum(v)/n for name,v in scores.items()}
    valid={name:means[name] for name in ("calendar","receipt","lag7")}
    best=min(valid.values())
    return {"world":label,"N_SYNTHETIC":n,"traffic_sha256":hashlib.sha256(json.dumps(counts).encode()).hexdigest(),
            "receipted_current":len(received),"selection_by_current_traffic":states,
            "available_only_receipt_loss":sum(received)/len(received) if received else None,
            "full_decision_receipt_loss":means["receipt"],"MAE":means,
            "regret_3_legal_policies":{name:value-best for name,value in valid.items()}}
def court():
    worlds={name:evaluate(name) for name in ("fast","congestion_delayed","uniform_60")}
    assert len({v["traffic_sha256"] for v in worlds.values()})==1
    selected=worlds["congestion_delayed"]
    return {"status":"SYNTHETIC_RECEIPT_AND_TRAFFIC_NOT_SOURCE_2025",
        "P21_matched_source_N_reference_ONLY":2121699,
        "authentic_client_receipt_logs":False,"authentic_provider_release_logs":False,
        "cryptographic_authenticity_verification":False,"same_synthetic_CSV_all_worlds":True,
        "worlds":worlds,
        "bounded_loss_B120":mean_bound(selected["receipted_current"],selected["N_SYNTHETIC"],
                                      selected["available_only_receipt_loss"],120),
        "worst_scenario_regret_within_these_3_options":{
          name:max(v["regret_3_legal_policies"][name] for v in worlds.values())
          for name in ("calendar","receipt","lag7")},
        "NO_CAUSAL_TRAFFIC_INTERVENTION_OR_INDIVIDUAL_WELFARE":True}
if __name__=="__main__":
    arg=argparse.ArgumentParser();arg.add_argument("--out",required=True,type=Path);a=arg.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(court(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("P23 synthetic receipt court only; original P21 N not replayed")
