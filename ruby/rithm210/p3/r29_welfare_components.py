"""R29 exact micro-macro welfare identity and Partial heldout decomposition.

For a conditional-independence six-actor forecast with probabilities p_i:
E[C(N)] = 24 + 3[(sum_i p_i - 4)^2 + sum_i p_i(1-p_i)].
This is a decomposition of a MODEL FORECAST, not a causal reduction of
realized group cost; omitted pairwise choice covariance is a live rival.
"""
from __future__ import annotations
import json,sys
import numpy as np
from scipy.special import expit
from r29_partial_information_cv import load,design,fit,SOURCE_SHA

def components(ps):
    p=np.asarray(ps,dtype=float)
    if p.shape!=(6,) or not np.all(np.isfinite(p)) or np.any((p<0)|(p>1)):
        raise ValueError('six valid actor probabilities required')
    mean=float(p.sum())
    variance=float(np.sum(p*(1-p)))
    displacement=(mean-4)**2
    return dict(occupancy_mean=mean,occupancy_variance=variance,
                squared_mean_displacement=displacement,
                expected_congestion=24+3*(displacement+variance))

def run(path):
    by=load(path)
    sessions=sorted(by)
    fold={s:i%6 for i,s in enumerate(sessions)}
    result={}
    for model in ('route_info_payoff','route_info_payoff_public'):
        summary={}
        for f in range(6):
            train=[s for s in sessions if fold[s]!=f]
            test=[s for s in sessions if fold[s]==f]
            X=[design(row[0],row[1],row[2],row[3],model)
               for s in train for group in by[s] for row in group]
            Y=[row[4] for s in train for group in by[s] for row in group]
            coef=fit(X,Y)
            for s in test:
                rows=[]
                for g in by[s]:
                    ps=expit(np.asarray([design(row[0],row[1],row[2],row[3],model) for row in g])@coef)
                    parts=components(ps)
                    observed=int(sum(row[4] for row in g))
                    actual=24+3*(observed-4)**2
                    rows.append([parts['occupancy_mean'],parts['occupancy_variance'],
                                 parts['squared_mean_displacement'],parts['expected_congestion'],
                                 actual,abs(parts['expected_congestion']-actual)])
                summary[s]=np.mean(rows,axis=0)
        result[model]=np.mean([summary[s] for s in sessions],axis=0).tolist()
    return {'source_sha256':SOURCE_SHA,'cohort':'24 published Partial sessions, t2..40',
            'columns':['predicted_mean_A','predicted_poisson_binomial_variance',
                       'predicted_squared_mean_distance_from_4','expected_cost',
                       'observed_cost','one_step_cost_MAE'],
            'result':result,
            'difference_public_minus_payoff':(np.array(result['route_info_payoff_public'])-
                np.array(result['route_info_payoff'])).tolist(),
            'identity':'independent P forecast: E[C]=24+3[(mu-4)^2+sum(p_i*(1-p_i))]; true choice covariance unmodeled',
            'interpretation':'Heldout aggregate decomposition, observational forecasts; no causal effects or cognition identified.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r29_welfare_components.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
