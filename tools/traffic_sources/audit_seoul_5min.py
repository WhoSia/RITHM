#!/usr/bin/env python3
"""Read ORIGINAL Seoul city five-minute source without zero-filling or welfare claims."""
import argparse, collections, csv, hashlib, json, math, statistics
from pathlib import Path

REQUIRED = ["기간", "노선 ID", "노선명", "구간 ID", "구간명", "구간 길이",
            "5분 코드", "교통량", "속도", "점유율"]

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def audit(source, encoding="cp949"):
    source=Path(source)
    seen=set()
    dates=collections.Counter()
    links=collections.Counter()
    valid_patterns=collections.Counter()
    missing=collections.Counter()
    speeds=collections.defaultdict(list)
    hour_speeds=collections.defaultdict(list)
    rows=0
    with source.open("r",encoding=encoding,newline="") as f:
        rdr=csv.DictReader(f)
        heads={x.strip():x for x in (rdr.fieldnames or [])}
        if any(x not in heads for x in REQUIRED):
            raise ValueError("Missing native source columns; do not guess a schema")
        for raw in rdr:
            v=lambda col:raw[heads[col]].strip()
            date,link,clock=v("기간"),v("구간 ID"),v("5분 코드").zfill(4)
            if (not date or not link or len(clock)!=4 or not clock.isdigit()
                    or int(clock[:2])>23 or int(clock[2:])>=60 or int(clock[2:])%5):
                raise ValueError("Invalid link/date/5-minute clock")
            key=(date,link,clock)
            if key in seen:
                raise ValueError("Duplicate source segment/date/clock")
            seen.add(key);rows+=1;dates[date]+=1;links[link]+=1
            available=[]
            for column in ("교통량","속도","점유율"):
                text=v(column)
                if not text:
                    missing[column]+=1
                    continue
                number=float(text)
                if not math.isfinite(number):
                    raise ValueError("Nonfinite observed value")
                if column=="교통량" and (number<0 or not number.is_integer()):
                    raise ValueError("Invalid vehicle count")
                if column=="속도" and not (0<number<=250):
                    raise ValueError("Invalid observed speed")
                if column=="점유율" and not 0<=number<=100:
                    raise ValueError("Invalid observed occupancy")
                available.append(column)
                if column=="속도":
                    speeds[(link,int(clock[:2]))].append(number)
                    hour_speeds[int(clock[:2])].append(number)
            valid_patterns["+".join(available)]+=1
    pairs=[]
    for link in links:
        a=speeds.get((link,1))
        b=speeds.get((link,7))
        if a and b:
            pairs.append(statistics.median(b)-statistics.median(a))
    return {
       "source_file":source.name,"source_sha256":sha256(source),
       "source_bytes":source.stat().st_size,"original_data_rows":rows,
       "dates":dict(dates),"source_segment_ids":len(links),
       "missing_observation_cells":dict(missing),
       "observed_patterns":dict(valid_patterns),
       "source_missing_segment_slots":sum(max(0,288*len(dates)-x) for x in links.values()) if len(dates)==1 else None,
       "matched_segment_hour_07_minus_01_speed_median_kmh":statistics.median(pairs) if pairs else None,
       "matched_segment_n":len(pairs),
       "matched_segment_negative":sum(x<0 for x in pairs),
       "matched_segment_zero":sum(x==0 for x in pairs),
       "hour_median_observed_speed_kmh":{str(hour):statistics.median(values)
            for hour,values in sorted(hour_speeds.items())},
       "forward_21_day_train_7_day_test_allowed":len(dates)>=28,
       "individual_human_welfare_identified":False,
       "guidance_causal_effect_identified":False,
       "source_length_unit_verified":False,
       "note":"One-day data/source average speed do not identify individual travel times. Missing flow is NOT zero."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("csv",type=Path)
    p.add_argument("--encoding",default="cp949")
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    report=audit(x.csv,x.encoding)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{report['original_data_rows']} rows, {report['source_segment_ids']} links; "
          f"{len(report['dates'])} day(s); 21+7 forward gate "
          f"{report['forward_21_day_train_7_day_test_allowed']}")
