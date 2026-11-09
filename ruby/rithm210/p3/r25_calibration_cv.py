"""RITHM R25: session-separated actor calibration -> six-person welfare.

Actor source rows are used locally but NEVER exported. Only session aggregate
metrics and training-fold model selections are written to JSON.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from r23_inertia_memory_cv import Actor, load_groups, evaluate
from r24_inertia_welfare_source import trained_choices
from r24_welfare_attribution import decompose
from r25_actor_calibration import CALIBRATORS, Calibrator, fit

def event_rows(groups, choices):
    """Generate strictly prior-only forecasts for both fixed model choices."""
    states={}
    events=[]
    for (s,section,t,g),players in sorted(groups.items()):
        people=sorted(players,key=lambda x:int(x['ID']))
        ids=[int(r['ID']) for r in people]
        if len(set(ids))!=6:raise ValueError('duplicate actors')
        trt=int(people[0]['trt'])
        y=[int(r['RouteA']) for r in people]
        if any(v not in (0,1) for v in y) or any(int(r['NumA'])!=sum(y) or int(r['trt'])!=trt for r in people):
            raise ValueError('bad or mixed group')
        actors=[states.setdefault((s,section,id),Actor()) for id in ids]
        if any(a.periods!=t-1 for a in actors):raise ValueError('period history discontinuity')
        for name,config in [('selected',choices[s,trt]),('frequency',(1.,5.,0.))]:
            records=[]
            for row,actor,actual in zip(people,actors,y):
                previous=actor.last_route
                d,strength,w=config
                forecast=(1-w)*actor.frequency(d)+w*actor.markov(strength)
                records.append(dict(session=s,treatment=trt,section=section,period=t,
                    group=g,model=name,p=forecast,y=actual,
                    prev=-1 if previous is None else previous,
                    informed=int(row['Informed'])))
            events.append(records)
        for actor,value in zip(actors,y):actor.update(value)
    return events


def group_score(records,calibrator):
    p=[calibrator.probability(r) for r in records]
    y=[r['y'] for r in records]
    previous=None if records[0]['period']==1 else [r['prev'] for r in records]
    return decompose(y,p,previous)


def choose_calibration(training_groups,training_sessions,variants=CALIBRATORS):
    """Five inner folds of 4 sessions each, each fitting on other 16."""
    training_sessions=sorted(training_sessions)
    if len(training_sessions)!=20:raise ValueError('need 20 independent training sessions')
    inner={s:i%5 for i,s in enumerate(training_sessions)}
    candidates={v:[] for v in variants}
    by_session=defaultdict(list)
    for records in training_groups:by_session[records[0]['session']].append(records)
    for fold in range(5):
        fit_sessions=[s for s in training_sessions if inner[s]!=fold]
        test_sessions=[s for s in training_sessions if inner[s]==fold]
        calibration_rows=[r for s in fit_sessions for group in by_session[s] for r in group]
        for variant in variants:
            model=fit(calibration_rows,variant)
            for s in test_sessions:
                scored=[group_score(group,model)['logloss'] for group in by_session[s]]
                candidates[variant].append(sum(scored)/len(scored))
    return min(variants,key=lambda v:(sum(candidates[v])/len(candidates[v]),v)),{
        v:sum(candidates[v])/len(candidates[v]) for v in variants}


def run(groups,draws=2000,seed=20261109):
    if draws<1:raise ValueError('draw count')
    raw_scores=evaluate(groups)
    choices,trace=trained_choices(raw_scores)
    sessions=sorted({key[0] for key in groups})
    folds={s:i%6 for i,s in enumerate(sessions)}
    events=event_rows(groups,choices)
    by_stm=defaultdict(list)
    for recs in events:
        r=recs[0]
        by_stm[r['session'],r['treatment'],r['model']].append(recs)
    scored=[];fold_plans=[]
    for fold in range(6):
        train=[s for s in sessions if folds[s]!=fold]
        test=[s for s in sessions if folds[s]==fold]
        for trt in (1,2,3):
            for name in ('frequency','selected'):
                training_groups=[g for s in train for g in by_stm[s,trt,name]]
                winner,inner=choose_calibration(training_groups,train)
                fitted=fit([r for g in training_groups for r in g],winner)
                fold_plans.append(dict(fold=fold,treatment=trt,model=name,
                    calibration=winner,training_sessions=20,heldout_sessions=4,
                    fitted_cells=len(fitted.shifts),inner_cv=inner))
                for s in test:
                    actual_groups=by_stm[s,trt,name]
                    for group in actual_groups:
                        before=group_score(group,Calibrator('identity',{}))
                        after=group_score(group,fitted)
                        scored.append(dict(session=s,treatment=trt,model=name,
                            period=group[0]['period'],raw=before,calibrated=after))
    if len(scored)!=5760*2:raise ValueError('exact source group coverage')
    metrics=('logloss','actor_brier','abs_cost_error','welfare_error',
             'linear','diagonal','same_pair','opposite_pair','unknown_pair',
             'mean_actor_error')
    per_session=defaultdict(list)
    for row in scored:per_session[row['session'],row['treatment'],row['model']].append(row)
    summaries=[]
    for trt in (1,2,3):
        for model in ('frequency','selected'):
            cohort=[per_session[s,trt,model] for s in sessions]
            assert all(cohort)
            output={}
            for metric in metrics:
                baseline=[sum(r['raw'][metric] for r in rs)/len(rs) for rs in cohort]
                calibrated=[sum(r['calibrated'][metric] for r in rs)/len(rs) for rs in cohort]
                differences=[b-a for a,b in zip(baseline,calibrated)]
                rng=__import__('random').Random(seed+trt+(0 if model=='frequency' else 10))
                boots=sorted(sum(rng.choice(differences) for _ in differences)/len(differences)
                             for _ in range(draws))
                output[metric]=dict(raw=sum(baseline)/24,calibrated=sum(calibrated)/24,
                    delta=sum(differences)/24,
                    bootstrap95=[boots[int(draws*.025)],boots[int(draws*.975)]])
            summaries.append(dict(treatment=trt,model=model,sessions=24,metrics=output))
    # Directly compare the two models on the SAME outer-heldout session support,
    # both before and after their individually train-fitted calibration maps.
    contrasts=[]
    for trt in (1,2,3):
        output={}
        for stage in ('raw','calibrated'):
            for metric in ('logloss','actor_brier','abs_cost_error','same_pair','opposite_pair'):
                contrasts_by_session=[]
                for session in sessions:
                    winner=per_session[session,trt,'selected']
                    baseline=per_session[session,trt,'frequency']
                    if len(winner)!=len(baseline):
                        raise ValueError('mismatched model group support')
                    diff=sum(r[stage][metric] for r in winner)/len(winner)-sum(
                        r[stage][metric] for r in baseline)/len(baseline)
                    contrasts_by_session.append(diff)
                rng=__import__('random').Random(seed+trt+(1 if stage=='calibrated' else 0))
                samples=sorted(sum(rng.choice(contrasts_by_session) for _ in sessions)/24
                               for _ in range(draws))
                output[f'{stage}_{metric}']=dict(delta=sum(contrasts_by_session)/24,
                    percentile95=[samples[int(draws*.025)],samples[int(draws*.975)]])
        contrasts.append(dict(treatment=trt,sessions=24,metrics=output))
    return dict(sessions=24,groups=5760,fold_plans=fold_plans,summaries=summaries,model_contrasts=contrasts,
       caveat='Exploratory historical data reused. Training-only 5x inner cross validation and 6x outer evaluation; no identified causal peer effects.')


def main():
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--draws',type=int,default=2000)
    p.add_argument('--output',default='r25_aggregate.json');args=p.parse_args()
    results=run(load_groups(args.source),draws=args.draws)
    Path(args.output).write_text(json.dumps(results,indent=2))
    for r in results['summaries']:
        m=r['metrics'];print(r['treatment'],r['model'],
            'logloss',round(m['logloss']['raw'],5),'->',round(m['logloss']['calibrated'],5),
            'actor_brier_delta',round(m['actor_brier']['delta'],5),
            'cost_mae_delta',round(m['abs_cost_error']['delta'],5),
            'same_pair_delta',round(m['same_pair']['delta'],4),
            'opposite_pair_delta',round(m['opposite_pair']['delta'],4))

if __name__=='__main__':main()
