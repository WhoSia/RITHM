"""RITHM R25: train-session-only regularized logit-offset probability calibration.

Never fit this layer on heldout actor outcomes. Features are predecision
previous route, treatment-specific Informed flag, and known period epoch.
"""
import math
from collections import defaultdict
from dataclasses import dataclass

CALIBRATORS = ('identity', 'global', 'route', 'route_epoch', 'route_informed', 'route_epoch_informed')
LAMBDA = 30.0  # fixed ex ante regularization; no outer-test tuning
EPS = 1e-9


def sigmoid(z):
    return 1.0/(1.0+math.exp(-z)) if z >= 0 else math.exp(z)/(1.0+math.exp(z))


def logit(p):
    p = min(1-EPS,max(EPS,p))
    return math.log(p/(1-p))


def epoch(period):
    return 'early' if period<=10 else 'middle' if period<=29 else 'late'


def cell(record, variant):
    if variant == 'identity': return None
    features = []
    if variant in ('route','route_epoch','route_informed','route_epoch_informed'):
        features.append(record['prev'])
    if variant in ('route_epoch','route_epoch_informed'):
        features.append(epoch(record['period']))
    if variant in ('route_informed','route_epoch_informed'):
        features.append(record['informed'])
    return tuple(features) if features else ('global',)


@dataclass(frozen=True)
class Calibrator:
    variant: str
    shifts: dict
    def probability(self, row):
        p = row['p']
        if self.variant == 'identity':return p
        return sigmoid(logit(p)+self.shifts.get(cell(row,self.variant),0.0))


def fit(rows,variant,lam=LAMBDA):
    if variant not in CALIBRATORS:raise ValueError('unknown calibration family')
    if not rows:raise ValueError('empty train')
    if not (math.isfinite(lam) and lam>0):raise ValueError('positive ridge shrinkage required')
    if variant == 'identity':return Calibrator(variant,{})
    grouped=defaultdict(list)
    for row in rows:
        if type(row['y']) is not int or row['y'] not in (0,1):raise ValueError('binary outcome')
        if not isinstance(row['p'],(float,int)) or not math.isfinite(row['p']) or not 0<=row['p']<=1:
            raise ValueError('invalid forecast')
        grouped[cell(row,variant)].append((logit(row['p']),row['y']))
    shifts={}
    for group,items in grouped.items():
        b=0.
        for _ in range(35):
            q=[sigmoid(z+b) for z,_ in items]
            g=sum(y-prob for (_,y),prob in zip(items,q))-lam*b
            h=sum(prob*(1-prob) for prob in q)+lam
            step=g/h
            b+=step
            if abs(step)<1e-11:break
        shifts[group]=b
    return Calibrator(variant,shifts)


