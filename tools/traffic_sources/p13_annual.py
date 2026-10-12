#!/usr/bin/env python3
"""RITHM P13-R2 annual forward sensor court; NumPy and standard library.
Requires H1 and H2 full 19-piece source folders each with manifest.json.
Scores observational sensor speed, flow, q/v; NEVER causal person welfare.
"""
import argparse,csv,datetime as dt,hashlib,json,warnings
from pathlib import Path
import numpy as np
DATES=[(dt.date(2025,1,1)+dt.timedelta(days=d)).strftime("%Y%m%d") for d in range(365)]
DIX={v:k for k,v in enumerate(DATES)}
HEADER=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME","HH5M_CD","VOL","SPD","OCC"]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for x in iter(lambda:f.read(8*1024*1024),b""):h.update(x)
 return h.hexdigest()
def load(roots):
 arr=(256,365,288);q=np.full(arr,np.nan,np.float32);v=np.full(arr,np.nan,np.float32)
 seen=np.zeros(arr,np.uint8);ids={};names={};stats={"rows":0,"missing_VOL":0,"missing_SPD":0,"missing_OCC":0}
 receipts=[]
 for root in map(Path,roots):
  manifest=json.loads((root/"manifest.json").read_text(encoding="utf8"))
  entries=manifest.get("parts_in_order",[])
  if manifest.get("format")!="RITHM_SOURCE_CSV_SHARDS_V1" or manifest.get("header")!=HEADER or len(entries)!=19:raise ValueError("Manifest contract")
  if [e["file"] for e in entries]!=[manifest["source_file"][:-4]+"__part_%03d.csv"%i for i in range(1,20)]:raise ValueError("Shard index order")
  if set(p.name for p in root.glob("*__part_*.csv"))!={e["file"] for e in entries}:raise ValueError("Missing/extra shards")
  total=0
  for e in entries:
   p=root/e["file"]
   if p.stat().st_size!=e["bytes"] or sha(p)!=e["sha256"]:raise ValueError("Shard SHA-256/byte mismatch")
   count=0
   with p.open(encoding="utf-8-sig",newline="") as f:
    rd=csv.DictReader(f)
    if rd.fieldnames!=HEADER:raise ValueError("Native header drift")
    for r in rd:
     d=DIX.get(r["DATE_CD"]);clock=r["HH5M_CD"].zfill(4)
     if d is None or len(clock)!=4 or not clock.isdigit() or int(clock[:2])>23 or int(clock[2:])>59 or int(clock[2:])%5:raise ValueError("Illegal date/5minute")
     tm=int(clock[:2])*12+int(clock[2:])//5
     key=r["LINK_ID"]
     if key not in ids:
      if len(ids)>=256:raise ValueError("Excess link IDs")
      ids[key]=len(ids);names[key]=(r["ROUTE_ID"],r["ROUTE_NAME"],r["ROAD_NAME"])
     elif names[key]!=(r["ROUTE_ID"],r["ROUTE_NAME"],r["ROAD_NAME"]):raise ValueError("Source ID drift")
     i=ids[key]
     if seen[i,d,tm]:raise ValueError("Duplicate link-date-clock source key")
     seen[i,d,tm]=1;count+=1
     for column,target in (("VOL",q),("SPD",v)):
      field=r[column].strip()
      if field=="":
       stats["missing_"+column]+=1;continue
      x=float(field)
      if not np.isfinite(x) or (column=="VOL" and (x<0 or int(x)!=x)) or (column=="SPD" and x<=0):raise ValueError("Invalid measured field")
      target[i,d,tm]=x
     if r["OCC"].strip()=="":
      stats["missing_OCC"]+=1
     else:
      occ=float(r["OCC"])
      if not np.isfinite(occ) or not 0<=occ<=100:raise ValueError("Invalid source occupancy")
   if count!=e["rows"]:raise ValueError("Author shard row count drift")
   total+=count
  if total!=manifest["record_count"]:raise ValueError("Total row count drift")
  stats["rows"]+=total
  receipts.append({"file":manifest["source_file"],"verified_shards":19,"logical_rows":total,
   "deleted_original_CP949_sha_manifest_only":manifest["original_sha256"]})
 n=len(ids);q=q[:n];v=v[:n];seen=seen[:n]
 daily=seen.sum(axis=(0,2))
 stats.update(links=n,theoretical_link_clock_bins=n*365*288,missing_link_clock_bins=n*365*288-stats["rows"],
  entire_network_absent_days=[DATES[j] for j in range(365) if daily[j]==0])
 return v,q,seen,stats,receipts
def admitted(seen,begin):
 count=seen.sum(axis=(0,2));nominal=seen.shape[0]*288
 return [{"day":DATES[d],"coverage":float(count[d]/nominal)}
         for d in range(begin,begin+28) if count[d]/nominal<.9]
def score(v,q,seen,begin):
 test=begin+21;bad=admitted(seen,begin)
 if bad:return {"status":"REJECT_COVERAGE","test_start":DATES[test],"bad":bad}
 tally=np.zeros(6,dtype=np.float64);n=0
 for day in range(test,test+7):
  dates=[d for d in range(begin,test) if d%7==day%7]
  with warnings.catch_warnings():
   warnings.simplefilter("ignore",RuntimeWarning)
   bv=np.nanmedian(v[:,dates,:],axis=1);bq=np.nanmedian(q[:,dates,:],axis=1)
  yy=v[:,day,:];qq=q[:,day,:]
  yprev=np.empty_like(yy);qprev=np.empty_like(qq)
  yprev[:,1:]=v[:,day,:-1];qprev[:,1:]=q[:,day,:-1]
  yprev[:,0]=v[:,day-1,287];qprev[:,0]=q[:,day-1,287]
  ok=np.isfinite(yy)&np.isfinite(qq)&np.isfinite(bv)&np.isfinite(bq)&np.isfinite(yprev)&np.isfinite(qprev)&(yy>0)&(bv>0)&(yprev>0)
  n+=int(ok.sum())
  for k,res in enumerate((yy-bv, yy-yprev, qq-bq, qq-qprev, qq/yy-bq/bv, qq/yy-qprev/yprev)):
   tally[k]+=float(np.abs(res[ok]).sum(dtype=np.float64))
 return {"status":"PASS","test_start":DATES[test],"n":n,
 **dict(zip(("speed_clock","speed_lag5","flow_clock","flow_lag5","proxy_clock","proxy_lag5"),(tally/n).tolist()))}
def two_clock(flow,seen,begin):
 test=begin+21;bad=admitted(seen,begin)
 if bad:return {"status":"REJECT_COVERAGE","test_start":DATES[test]}
 n=flow.shape[0];f=flow.reshape(n,-1)
 lo=max(2,begin*288);te=test*288;end=(test+7)*288
 y=f[:,lo:end];f5=f[:,lo-1:end-1];f10=f[:,lo-2:end-2]
 valid=np.isfinite(y)&np.isfinite(f5)&np.isfinite(f10)
 split=te-lo;old=valid[:,:split]
 e5=np.where(old,np.abs(y[:,:split]-f5[:,:split]),0.).sum(axis=1)
 e10=np.where(old,np.abs(y[:,:split]-f10[:,:split]),0.).sum(axis=1)
 choose_train=(e10<e5)&(old.sum(axis=1)>0)
 delta=np.where(valid,np.abs(y-f5)-np.abs(y-f10),0.).astype(np.float64)
 C=np.concatenate((np.zeros((n,1)),np.cumsum(delta,axis=1)),axis=1)
 N=np.concatenate((np.zeros((n,1),dtype=np.int32),np.cumsum(valid.astype(np.int32),axis=1)),axis=1)
 t=np.arange(split,end-lo);t0=np.maximum(0,t-288)
 choose_live=((C[:,t]-C[:,t0])>0)&((N[:,t]-N[:,t0])>=144)
 obs=y[:,split:];a=f5[:,split:];b=f10[:,split:];ok=valid[:,split:]
 return {"status":"PASS","test_start":DATES[test],"n":int(ok.sum()),
  "lag5":float(np.abs(obs[ok]-a[ok]).mean()),"lag10":float(np.abs(obs[ok]-b[ok]).mean()),
  "train_selected":float(np.abs(obs[ok]-np.where(choose_train[:,None],b,a)[ok]).mean()),
  "online_24h":float(np.abs(obs[ok]-np.where(choose_live,b,a)[ok]).mean()),
  "train_selected_10min_links":int(choose_train.sum())}
def run(h1,h2):
 v,q,seen,stats,receipts=load((h1,h2))
 w=[score(v,q,seen,t) for t in range(0,338,28)]
 x=[two_clock(q,seen,t) for t in range(0,338,28)]
 good=[z for z in w if z["status"]=="PASS"];explore=[z for z in x if z["status"]=="PASS"]
 def weighted(a,key):return sum(z["n"]*z[key] for z in a)/sum(z["n"] for z in a)
 return {"source_stats":stats,"manifest_receipts":receipts,"thirteen_fixed_windows":w,
  "source_exposed_exploratory_experts":x,
  "summary":{"pass":len(good),"rejected":13-len(good),"paired":sum(z["n"] for z in good),
   **{k:weighted(good,k) for k in ("speed_clock","speed_lag5","flow_clock","flow_lag5","proxy_clock","proxy_lag5")},
   "exploratory_paired":sum(z["n"] for z in explore),
   **{k:weighted(explore,k) for k in ("lag5","lag10","train_selected","online_24h")}},
  "welfare":"q/v is link flow/speed proxy, NOT realized person trip cost",
  "guidance_causal_effect":"NOT IDENTIFIED"}
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for k in ("h1","h2","out"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();result=run(a.h1,a.h2)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
 print(json.dumps(result["summary"],ensure_ascii=False,indent=2))
