#!/usr/bin/env python3
"""Reproduce integer near-flat redistribution sensitivity from original 2025 shards.

All input files must already be authenticated with the frozen source SHA manifest
gate, prior to this program. This is NOT a measured sensor-correction algorithm.
Usage:
  PYTHONPATH=src python tools/traffic_sources/phase_budget_audit.py \
      --source-dir /drive-shards --days 20250212 20250323 20250416 20250418 20250419 20250421 \
      --out /scratch/p16_budget.json
"""
import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
from rithm.observation import minimal_balancing_transfer

HEADER=["DATE_CD","ROUTE_ID","ROUTE_NAME","LINK_ID","ROAD_NAME","HH5M_CD","VOL","SPD","OCC"]

def audit_parts(paths, dates):
    dates=set(dates)
    if not dates or not paths:
        raise ValueError("At least one source part and target day required")
    rows=defaultdict(dict)
    allfiles=set()
    for file in paths:
        file=Path(file)
        if file in allfiles:
            raise ValueError("duplicate source file")
        allfiles.add(file)
        with file.open(encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if reader.fieldnames!=HEADER:
                raise ValueError("unexpected 2025 source native schema")
            for x in reader:
                day=x["DATE_CD"]
                if day not in dates:
                    continue
                hhmm=x["HH5M_CD"].zfill(4)
                if not (len(hhmm)==4 and hhmm.isdigit() and int(hhmm[:2])<24
                        and int(hhmm[2:])<60 and int(hhmm[2:])%5==0):
                    raise ValueError("invalid five-minute slot")
                if x["VOL"].strip()=="":
                    continue
                vol=int(x["VOL"])
                if vol<0:
                    raise ValueError("negative measured volume")
                slot=int(hhmm[:2])*12+int(hhmm[2:])//5
                key=(day,x["ROUTE_ID"],x["LINK_ID"])
                if slot in rows[key]:
                    raise ValueError("duplicate source link/date/slot")
                rows[key][slot]=vol
    daily={}
    for day in sorted(dates):
        pairs=volume=transfers=0
        signs=[]
        hour_groups=defaultdict(list)
        for (d,route,link),src in rows.items():
            if d!=day:
                continue
            signed=0
            matched=0
            for idx in range(144):
                a,b=2*idx,2*idx+1
                if a not in src or b not in src:
                    continue
                x,y=src[a],src[b]
                pairs+=1
                volume+=x+y
                transfers+=minimal_balancing_transfer(x,y)
                signed+=y-x
                matched+=1
                hour_groups[(route,idx//6)].append(y-x)
            if matched:
                signs.append(signed)
        if not pairs:
            raise ValueError("target source day absent from input parts")
        directions={}
        for hour in (8,9,10,11,12):
            route_means=[sum(a)/len(a) for (route,h),a in hour_groups.items()
                         if h==hour]
            directions[str(hour)]={"groups":len(route_means),
                                  "odd_higher":sum(v>0 for v in route_means),
                                  "even_higher":sum(v<0 for v in route_means)}
        daily[day]={"matched_ten_min_pairs":pairs,
             "source_link_day_groups":len(signs),
             "observed_5min_section_passage_sum":volume,
             "minimum_integer_bin_reassignments_if_latent_near_flat":transfers,
             "minimum_fraction_of_source_section_passages":transfers/volume,
             "signed_link_odd_higher":sum(v>0 for v in signs),
             "signed_link_even_higher":sum(v<0 for v in signs),
             "hourly_route_direction_signs":directions}
    return {"scientific_status":"conditional near-flat latent reconstruction; physical origin NOT identified",
            "source_days":daily,
            "no_causal_sensor_error_claim":True,
            "source_unit":"section-passages; NOT unique vehicles",
            "missing_source_count_is_not_zero":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--days",nargs="+",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    parts=sorted(args.source_dir.glob("*__part_*.csv"))
    result=audit_parts(parts,args.days)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"audited {len(result['source_days'])} source dates across {len(parts)} shards")

if __name__=="__main__":
    main()
