#!/usr/bin/env python3
"""RITHM P13: exact 21d/7d source-clock legal Seoul five-minute forecast.
Only observed link/sensor speed+flow and q/v, NEVER actual individual welfare.
Python standard library, no external dependencies or credentials.
"""
import argparse,csv,datetime as dt,hashlib,json,collections,statistics,math
from pathlib import Path
HEADER=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME","HH5M_CD","VOL","SPD","OCC"]
class SourceError(ValueError): pass
def sha(path):
    with open(path,"rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def med(v):return (statistics.median(q for q,s in v),statistics.median(s for q,s in v))
def sample(row):
    if len(row)!=9:raise SourceError("source schema length")
    date,route,rname,link,lname,clock,q,v,occ=row
    if not (len(date)==8 and date.isdigit() and route and link):raise SourceError("source date/id")
    day=dt.datetime.strptime(date,"%Y%m%d").date()
    if not clock.isdigit():raise SourceError("source 5m clock")
    clock=clock.zfill(4);hh=int(clock[:2]);mm=int(clock[2:])
    if hh>23 or mm>55 or mm%5:raise SourceError("source clock not 5m")
    try: q=int(q) if q.strip() else None
    except ValueError:raise SourceError("source count")
    try: v=float(v) if v.strip() else None
    except ValueError:raise SourceError("source speed")
    if q is not None and q<0:raise SourceError("negative vehicles")
    if v is not None and (not math.isfinite(v) or v<0 or v>250):raise SourceError("invalid speed")
    if occ.strip():
        try: o=float(occ)
        except ValueError:raise SourceError("invalid occupancy")
        if not math.isfinite(o) or not 0<=o<=100:raise SourceError("invalid occupancy")
    return day,(route,link),hh*60+mm,q,v
def verify(manifest,source_dir,indices):
    m=json.loads(Path(manifest).read_text(encoding="utf8"))
    if m.get("header")!=HEADER or m.get("part_count")!=19:raise SourceError("wrong author split manifest")
    if m.get("source_file") not in (
        "2025년 도시고속도로 5분단위 링크 속도_상반기.csv",
        "2025년 도시고속도로 5분단위 링크 속도_하반기.csv"):
        raise SourceError("unknown half-year source")
    selected=[]
    for index in indices:
        item=m["parts_in_order"][index-1];p=Path(source_dir)/item["file"]
        if not p.is_file() or p.stat().st_size!=item["bytes"] or sha(p)!=item["sha256"]:
            raise SourceError(f"source shard {index} missing or hash mismatched")
        selected.append((p,item))
    return m,selected
def st():return [0,0.,0.,0.]
def add(s,q,v,pq,pv):
    s[0]+=1;s[1]+=abs(q-pq);s[2]+=abs(v-pv);s[3]+=abs(q/v-pq/pv)
def finish(s):
    return {"n":s[0],"flow_mae_vehicles_per_5m":s[1]/s[0] if s[0] else None,
        "speed_mae_kmh":s[2]/s[0] if s[0] else None,
        "ratio_proxy_mae_vehicle_hours_per_km":s[3]/s[0] if s[0] else None}
def run(manifest,source_dir,start,begin,end):
    start=dt.date.fromisoformat(start);train_end=start+dt.timedelta(days=21);test_end=train_end+dt.timedelta(days=7)
    m,source=verify(manifest,source_dir,range(begin,end+1))
    slot=collections.defaultdict(list);fallback=collections.defaultdict(list)
    global_by_link=collections.defaultdict(list);test=[]
    last_clock={};last_day=None;days=set()
    for path,item in source:
        count=0
        with path.open("r",encoding="utf-8-sig",newline="") as f:
            rd=csv.reader(f,strict=True)
            if next(rd)!=HEADER:raise SourceError("source header drift")
            for row in rd:
                count+=1
                day,k,clock,q,v=sample(row)
                if last_day is not None and day<last_day:raise SourceError("source dates regress")
                last_day=day
                old=last_clock.get((day,k))
                if old is not None and clock<=old:raise SourceError("source duplicate or clock order")
                last_clock[(day,k)]=clock
                days.add(day)
                if q is None or v is None or v<=0:continue
                if start<=day<train_end:
                    slot[(k,day.weekday(),clock)].append((q,v))
                    fallback[(k,clock)].append((q,v))
                    global_by_link[k].append((q,v))
                elif train_end<=day<test_end:test.append((day,k,clock,q,v))
        if count!=item["rows"]:raise SourceError("source shard record count drift")
    if any(start+dt.timedelta(days=i) not in days for i in range(28)):
        raise SourceError("28 day calendar window contains unobserved source date")
    traincounts=collections.Counter()
    for (k,clock),v in fallback.items():traincounts[k]+=len(v)
    testcounts=collections.Counter(k for day,k,clock,q,v in test)
    eligible={k for k,n in traincounts.items() if n>=21*288//2 and testcounts[k]>=7*288//2}
    byslot={k:med(v) for k,v in slot.items() if k[0] in eligible}
    byclock={k:med(v) for k,v in fallback.items() if k[0] in eligible}
    bylink={k:med(v) for k,v in global_by_link.items() if k in eligible}
    previous={};paired_clock=st();paired_prior=st();clockall=st()
    linkmetrics=collections.defaultdict(lambda:[st(),st()])
    daymetrics=collections.defaultdict(lambda:[st(),st()])
    for day,k,clock,q,v in test:
        if k not in eligible:continue
        pred=byslot.get((k,day.weekday(),clock),byclock.get((k,clock),bylink[k]))
        pq,pv=pred;add(clockall,q,v,pq,pv)
        when=dt.datetime.combine(day,dt.time(clock//60,clock%60))
        old=previous.get(k)
        if old and old[0]==when-dt.timedelta(minutes=5):
            add(paired_clock,q,v,pq,pv);add(paired_prior,q,v,old[1],old[2])
            add(linkmetrics[k][0],q,v,pq,pv);add(linkmetrics[k][1],q,v,old[1],old[2])
            add(daymetrics[day.isoformat()][0],q,v,pq,pv)
            add(daymetrics[day.isoformat()][1],q,v,old[1],old[2])
        previous[k]=(when,q,v)
    if paired_clock[0]<10000:raise SourceError("unreliable paired evaluation size")
    return {"source":m["source_file"],"shard_numbers":list(range(begin,end+1)),
      "source_original_cp949_binary_sha_reverifiable":False,
      "train_from":start.isoformat(),"test_from":train_end.isoformat(),
      "test_end_exclusive":test_end.isoformat(),"eligible_link_count":len(eligible),
      "clock_all_observations":finish(clockall),
      "paired_same_sensor_times":{"train_only_weekday_time_median":finish(paired_clock),
        "last_actual_observed_5min":finish(paired_prior)},
      "per_link":{f"{k[0]}|{k[1]}":{"clock":finish(a),"prior5":finish(b)}
                   for k,(a,b) in linkmetrics.items()},
      "per_day":{k:{"clock":finish(a),"prior5":finish(b)} for k,(a,b) in daymetrics.items()},
      "actual_human_welfare_identified":False,
      "VMS_info_guidance_causal_effect_identified":False,
      "metric_qualifier":"q/v is vehicles*hours/km per link/bin proxy; driver traversal times unmeasured",
      "clock_semantics":"last actual 5-min observation is teacher-forced one-step, not rollout"}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",required=True,type=Path);p.add_argument("--parts-dir",required=True,type=Path)
    p.add_argument("--train-start",required=True);p.add_argument("--part-start",type=int,required=True)
    p.add_argument("--part-end",type=int,required=True);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();r=run(a.manifest,a.parts_dir,a.train_start,a.part_start,a.part_end)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps({k:v for k,v in r.items() if k not in ("per_link","per_day")},ensure_ascii=False))
if __name__=="__main__":main()
