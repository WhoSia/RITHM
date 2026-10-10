#!/usr/bin/env python3
"""Decode CC-BY human route/cost inputs from Wijayaratna et al. 2017 S2 data.

Source: https://doi.org/10.1371/journal.pone.0184191.s002
All data are public and author-credited; never alter recorded individual costs.
"""
from pathlib import Path
import csv
import pandas as pd

ROOT=Path(__file__).resolve().parent
DIGITS="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def decode(routes=None,costs=None):
    routes=Path(routes) if routes is not None else ROOT/'data'/'rithm23_wijayaratna2017_routes.csv'
    costs=Path(costs) if costs is not None else ROOT/'data'/'rithm23_wijayaratna2017_costs_packed.csv'
    with routes.open(newline='',encoding='utf-8') as f: rr=list(csv.DictReader(f))
    cc={}
    with costs.open(newline='',encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row:continue
            sid,g,stage,code,agg=row
            key=(sid,int(g),int(stage))
            assert key not in cc and len(code)==240
            cc[key]=([11+DIGITS.index(ch) for ch in code],int(agg))
    assert len(rr)==len(cc)==24
    out=[]
    for r in rr:
        key=(r['session'],int(r['group']),int(r['stage']))
        costs_,aggregate=cc[key]
        assert sum(costs_)==aggregate==int(r['group_stage_total_cost'])
        value=int(r['choices_base3_hex'],16); paths=[]
        for i in range(240):
            value,digit=divmod(value,3);paths.append(digit+1)
        assert value==0
        paths=paths[::-1]
        incident=format(int(r['incident_20_bits_hex'],16),'020b')
        assert incident.count('1')==4
        for t in range(20):
            route=paths[t*12:(t+1)*12]
            recorded=costs_[t*12:(t+1)*12]
            n=[route.count(i) for i in (1,2,3)]
            assert len(route)==len(recorded)==12 and sum(n)==12
            for i in range(12):
                out.append(dict(session=key[0],group=key[1],stage=key[2],info=int(r['info']),
                    t=t+1,person=i+1,route=route[i],cost=recorded[i],z=int(incident[t]),
                    n1=n[0],n2=n[1],n3=n[2]))
    assert len(out)==5760
    return pd.DataFrame(out)
