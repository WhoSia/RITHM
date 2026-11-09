"""RITHM R23D: heldout-model selection fixed before epoch scoring.

Observational diagnosis: how inertia's group forecast changes across periods;
models are chosen on all TRAINING sessions only, never on heldout epochs.
"""
from collections import defaultdict
from r23_inertia_memory_cv import Actor, candidates, evaluate, label, load_groups, scores


def epoch(period: int) -> str:
    if not 1 <= period <= 40:
        raise ValueError('period outside 1..40')
    return 'early' if period <= 10 else ('middle' if period <= 29 else 'late')


def assess(groups, *, cv_rows=None):
    configs = candidates()
    cv_rows = evaluate(groups) if cv_rows is None else cv_rows
    sessions = sorted({r['session'] for r in cv_rows['session_results']})
    if len(sessions) != 24:
        raise ValueError('24 independent source sessions needed')
    lookup = {(r['session'], r['treatment'],r['model']):r for r in cv_rows['session_results']}
    names = {label(c):c for c in configs}
    winners={}
    for k,s in enumerate(sessions):
        fold=k%6
        train=[other for j,other in enumerate(sessions) if j%6!=fold]
        for trt in (1,2,3):
            winners[(s,trt)] = min(names, key=lambda m: (
                sum(lookup[(t,trt,m)]['logloss'] for t in train)/20.0,m))
    states={}
    sums=defaultdict(lambda:[0.,0.,0.,0.,0.,0.,0])
    for (s,section,period,group),people in sorted(groups.items()):
        people=sorted(people,key=lambda r:int(r['ID']))
        n=sum(int(r['RouteA']) for r in people)
        if any(int(r['NumA'])!=n for r in people):
            raise ValueError('group occupancy invalid')
        trt=int(people[0]['trt'])
        actors=[states.setdefault((s,section,int(r['ID'])),Actor()) for r in people]
        if any(a.periods!=period-1 for a in actors):
            raise ValueError('future outcome appeared in history')
        config=names[winners[(s,trt)]]
        mix_ps=[(1-config[2])*a.frequency(config[0])+config[2]*a.markov(config[1])
                for a in actors]
        base_ps=[a.frequency(1.0) for a in actors]
        mix=scores(mix_ps,n);base=scores(base_ps,n)
        entry=sums[(s,trt,epoch(period))]
        entry[0]+=mix[0];entry[1]+=base[0]
        entry[2]+=mix[1];entry[3]+=base[1]
        entry[4]+=mix[2];entry[5]+=base[2]
        entry[6]+=1
        for actor,r in zip(actors,people):
            actor.update(int(r['RouteA']))
    by=defaultdict(list)
    for (s,trt,which),row in sums.items():
        if not row[6]: raise ValueError('missing epoch')
        by[(trt,which)].append(tuple(x/row[6] for x in row[:6]))
    output=[]
    for (trt,which),rows in sorted(by.items()):
        if len(rows)!=24: raise ValueError('missing session in epoch')
        output.append(dict(treatment=trt,epoch=which,sessions=len(rows),
           delta_logloss=sum(a-b for a,b,*_ in rows)/24,
           delta_brier=sum(row[2]-row[3] for row in rows)/24,
           delta_cost_abs_error=sum(row[4]-row[5] for row in rows)/24))
    return output


if __name__=='__main__':
    import json,sys
    print(json.dumps(assess(load_groups(sys.argv[1])),indent=2))
