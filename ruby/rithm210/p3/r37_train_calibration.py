"""R37 train-session-only calibration of published author Appendix-B SSM predictors.

This adds a separately labelled RITHM wrapper (0.5 mixture), not a claim
that the original SSM algorithm itself has this parameter. Sixfold original
24 session anchored folds; no held-out sessions influence epsilon choice.
"""
import json,sys
from collections import defaultdict
import numpy as np
from r37_ssm_source_cv import run,group_metrics
EPS_GRID=(0.,.05,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.)

def train_calibration(path):
    plain,groups=run(path,True)
    sessions=sorted(groups);fold={sid:i%6 for i,sid in enumerate(sessions)}
    results={}
    for column,name in enumerate(('SSM5','SSM1-9_fixed_q_posterior')):
        # Fixed model predictor histories. Epsilon only affects out-of-sample
        # probability forecast, not original SSM q posterior learning rule.
        scores={}
        for sid in sessions:
            a=np.asarray([row[column] for row in groups[sid]])
            y=np.asarray([row[2] for row in groups[sid]])
            if a.shape[1:]!=(6,) or y.shape!=a.shape:raise ValueError('unexpected source layout')
            scores[sid]={}
            for e in EPS_GRID:
                p=np.clip(a*(1-e)+e*.5,1e-12,1-1e-12)
                log=-y*np.log(p)-(1-y)*np.log1p(-p)
                scores[sid][e]=float(log.mean())
        selection=[];estimated={};probs={}
        for f in range(6):
            train=[s for s in sessions if fold[s]!=f]
            test=[s for s in sessions if fold[s]==f]
            if len(train)!=20 or len(test)!=4:raise ValueError('fold error')
            candidate={e:float(np.mean([scores[s][e] for s in train])) for e in EPS_GRID}
            eps=min(EPS_GRID,key=lambda x:(candidate[x],x))
            selection.append({'fold':f,'epsilon':eps,'training_actor_logloss':candidate[eps]})
            for sid in test:
                p=np.asarray([row[column] for row in groups[sid]])*(1-eps)+eps*.5
                y=np.asarray([row[2] for row in groups[sid]])
                estimated[sid]=np.mean([group_metrics(a,b) for a,b in zip(p,y)],axis=0)
                probs[sid]=p
        metrics=np.mean([estimated[s] for s in sessions],axis=0)
        results[name]={'calibrated_metrics':metrics.tolist(),'selection':selection,'raw_metrics':plain['results'][name]['metrics'],
         'improvement':(metrics-np.asarray(plain['results'][name]['metrics'])).tolist()}
    return {'source_sha256':plain['source_sha256'],'pop':plain['scoring'],
        'metric_names':plain['metrics'],'epsilon_grid':EPS_GRID,'models':results,
        'calibration_interpretation':'Separately labelled 0.5 predictive mixture; not the author original mechanism. Epsilon chosen solely on 20 train sessions per fold. No actor/choice held-out target used in choosing epsilon.',
        'cautions':['RITHM models are fitted, SSM mechanisms fixed q; this calibrator partially addresses score sharpness but not equal parameter complexity','Original author EWA-lite remains unimplemented, do not claim a 3-way complete contest','SSM1-9 actor-q posterior uses uncalibrated conditional SSM likelihood by declared design']}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r37_train_calibration.py PRIVATE_CSV')
    print(json.dumps(train_calibration(sys.argv[1]),indent=2))