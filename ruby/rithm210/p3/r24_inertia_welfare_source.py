"""RITHM R24: apply R23's 33 trained-only inertia candidates to R24 welfare.

Source remains local SHA-sealed; outputs only aggregate session/epoch statistics.
Never interpret residual cross-products as identified strategic dependence.
"""
import json
import random
import sys
from collections import defaultdict

from r23_inertia_memory_cv import Actor,candidates,evaluate,label,load_groups
from r24_welfare_attribution import decompose

def trained_choices(scores):
    rows=scores['session_results']
    sessions=sorted({r['session'] for r in rows})
    if len(sessions)!=24:raise ValueError('24 sessions required')
    configurations={label(c):c for c in candidates()}
    index={(r['session'],r['treatment'],r['model']):r for r in rows}
    if len(index)!=len(rows):raise ValueError('duplicate session scores')
    result={}
    folds=[]
    for fold in range(6):
        train=[s for i,s in enumerate(sessions) if i%6!=fold]
        test=[s for i,s in enumerate(sessions) if i%6==fold]
        assert len(train)==20 and len(test)==4
        for treatment in (1,2,3):
            best=min(configurations,key=lambda name:(
                sum(index[s,treatment,name]['logloss'] for s in train)/len(train),name))
            folds.append(dict(fold=fold,treatment=treatment,
                              model=best,training_sessions=20,heldout_sessions=4))
            for session in test:result[session,treatment]=configurations[best]
    if len(result)!=72:raise ValueError('fold coverage')
    return result,folds

def residual_rows(groups,choices):
    states={}
    out=[]
    for (session,section,period,group),people in sorted(groups.items()):
        ordered=sorted(people,key=lambda r:int(r['ID']))
        ids=[int(r['ID']) for r in ordered]
        if len(set(ids))!=6:raise ValueError('duplicate actor')
        treatment=int(ordered[0]['trt'])
        outcomes=[int(r['RouteA']) for r in ordered]
        if any(int(r['NumA'])!=sum(outcomes) or int(r['trt'])!=treatment
               for r in ordered):
            raise ValueError('group occupancy/treatment mismatch')
        actors=[states.setdefault((session,section,id),Actor()) for id in ids]
        if any(actor.periods!=period-1 for actor in actors):
            raise ValueError('actor history discontinuity')
        previous=None if period==1 else [actor.last_route for actor in actors]
        if period>1 and any(route is None for route in previous):
            raise ValueError('missing previous route')
        for model,config in [
            ('selected',choices[session,treatment]),('frequency',(1.,5.,0.))]:
            ps=[(1-config[2])*actor.frequency(config[0])+
                config[2]*actor.markov(config[1]) for actor in actors]
            result=decompose(outcomes,ps,previous)
            out.append(dict(session=session,treatment=treatment,period=period,
                            model=model,**result))
        # Crucial: neither current route nor partner route was used in p_i.
        for actor,y in zip(actors,outcomes):actor.update(y)
    return out

METRICS=('welfare_error','linear','diagonal','same_pair','opposite_pair',
         'unknown_pair','abs_cost_error','logloss','actor_brier','mean_actor_error')

def summaries(rows,draws=4000,seed=20261109):
    if draws<1:raise ValueError('draws')
    by=defaultdict(list)
    for row in rows:
        age='early' if row['period']<=10 else (
            'middle' if row['period']<=29 else 'late')
        by[row['session'],row['treatment'],row['model']].append(row)
    all_out=[]
    for treatment in (1,2,3):
        sessions=sorted({s for s,t,m in by if t==treatment})
        if len(sessions)!=24:raise ValueError('24 independent sessions')
        metrics={}
        for name in METRICS:
            differences=[]
            for session in sessions:
                a=by[session,treatment,'selected']
                b=by[session,treatment,'frequency']
                if len(a)!=len(b):raise ValueError('unpaired period groups')
                differences.append(sum(x[name] for x in a)/len(a)-
                                   sum(x[name] for x in b)/len(b))
            rng=random.Random(seed+treatment)
            samples=sorted(sum(rng.choice(differences) for _ in differences)/
                           len(differences) for _ in range(draws))
            metrics[name]=dict(mean_difference=sum(differences)/len(differences),
                               percentile95=[samples[int(draws*.025)],
                                             samples[int(draws*.975)]],
                               sessions_candidate_better=sum(x<0 for x in differences))
        all_out.append(dict(treatment=treatment,sessions=24,metrics=metrics))
    epochs=[]
    for (treatment,model),records in sorted(
        {(r['treatment'],r['model']) for r in rows}):
        for age,rule in [('early',lambda p:p<=10),
                         ('middle',lambda p:11<=p<=29),
                         ('late',lambda p:p>=30)]:
            subset=[r for r in rows if r['treatment']==treatment and
                    r['model']==model and rule(r['period'])]
            epochs.append(dict(treatment=treatment,model=model,epoch=age,
                groups=len(subset),
                **{name:sum(r[name] for r in subset)/len(subset)
                   for name in METRICS}))
    return dict(session_paired=all_out,epoch_group_weighted=epochs)

def run(path):
    groups=load_groups(path)
    options,folds=trained_choices(evaluate(groups))
    rows=residual_rows(groups,options)
    if len(rows)!=5760*2:raise ValueError('expected 5760 groups x 2')
    return dict(source_groups=5760,sessions=24,fold_choices=folds,
                **summaries(rows),
                caveat='Reused exploratory source; residual pairs are not identified causal dependence. Period 1 pairs are unclassified.')

if __name__=='__main__':
    print(json.dumps(run(sys.argv[1]),indent=2))
