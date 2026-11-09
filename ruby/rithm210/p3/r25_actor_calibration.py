"""RITHM R25: train-session-only regularized logit-offset calibration."""
import math
from collections import defaultdict
from dataclasses import dataclass

CALIBRATORS=('identity','global','route','route_epoch','route_informed','route_epoch_informed')
LAMBDA=30.0
EPS=1e-9

def sigmoid(z):
    return 1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))

def logit(p):
    p=min(1-EPS,max(EPS,p))
    return math.log(p/(1-p))

def epoch(t):
    return 'early' if t<=10 else ('middle' if t<=29 else 'late')

def cell(row,variant):
    if variant=='identity':return None
    features=[]
    if variant in ('route','route_epoch','route_informed','route_epoch_informed'):
        features.append(row['prev'])
    if variant in ('route_epoch','route_epoch_informed'):
        features.append(epoch(row['period']))
    if variant in ('route_informed','route_epoch_informed'):
        features.append(row['informed'])
    return tuple(features) if features else ('global',)

@dataclass(frozen=True)
class Calibrator:
    variant:str
    shifts:dict
    def probability(self,row):
        p=row['p']
        if self.variant=='identity':return p
        return sigmoid(logit(p)+self.shifts.get(cell(row,self.variant),0.))

def fit(rows,variant,lam=LAMBDA):
    if variant not in CALIBRATORS:raise ValueError('unknown calibration family')
    if not rows:raise ValueError('empty train')
    if not (math.isfinite(lam) and lam>0):raise ValueError('positive ridge shrinkage')
    if variant=='identity':return Calibrator(variant,{})
    grouped=defaultdict(list)
    for r in rows:
        if type(r['y']) is not int or r['y'] not in (0,1):raise ValueError('binary outcome')
        if not isinstance(r['p'],(float,int)) or not math.isfinite(r['p']) or not 0<=r['p']<=1:
            raise ValueError('invalid forecast')
        grouped[cell(r,variant)].append((logit(r['p']),r['y']))
    shifts={}
    for key,items in grouped.items():
        b=0.
        for _ in range(35):
            q=[sigmoid(z+b) for z,_ in items]
            g=sum(y-prob for (_,y),prob in zip(items,q))-lam*b
            h=sum(prob*(1-prob) for prob in q)+lam
            delta=g/h
            b+=delta
            if abs(delta)<1e-11:break
        shifts[key]=b
    return Calibrator(variant,shifts)
