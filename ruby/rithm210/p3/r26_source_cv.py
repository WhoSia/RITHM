"""R26 original-source heldout latent dependency compared with R25 calibration.

Outcomes of heldout sessions NEVER affect original actor selection, marginal
calibration, or latent tau selection. A common group innovation remains a
statistical surrogate, never a claim of strategic coordination.
"""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from random import Random
from r23_inertia_memory_cv import load_groups,evaluate
from r24_inertia_welfare_source import trained_choices
from r25_calibration_cv import event_rows,choose_calibration
from r25_actor_calibration import fit
from r26_common_shock import forecast,candidates
from r26_fast_batch import loglosses

METRICS=('logloss','joint_logloss','brier','cost_mae','cost_bias','actor_brier')


def projected(groups,calibrator):
    projected_groups=[]
    for group in groups:
        ps=[calibrator.probability(r) for r in group]
        y=[r['y'] for r in group]
        prev=[r['prev'] for r in group]
        projected_groups.append((ps,y,prev,group[0]['session'],group[0]['period']))
    return projected_groups


def training_shock_choice(training_groups,training_sessions,calibration_variant,
                          shock_candidates=None):
    """Choose latent family/tau using five OOF train-session folds (16/4 each).

    calibration_variant itself was chosen by a separate prior-only inner CV on
    the same 20 outer-train sessions. Outer heldout outcomes never participate.
    """
    training_sessions=sorted(training_sessions)
    if len(training_sessions)!=20 or len(set(training_sessions))!=20:
        raise ValueError('need twenty distinct training sessions')
    shock_candidates=candidates() if shock_candidates is None else tuple(shock_candidates)
    if not shock_candidates or len(set(shock_candidates))!=len(shock_candidates):
        raise ValueError('unique candidates required')
    by=defaultdict(list)
    for group in training_groups:
        if len(group)!=6:raise ValueError('six group actor records')
        sid=group[0]['session']
        if sid not in training_sessions:raise ValueError('nontraining session leaked into shock tuning')
        by[sid].append(group)
    if sorted(by)!=training_sessions:raise ValueError('training session coverage mismatch')
    fold_of={s:i%5 for i,s in enumerate(training_sessions)}
    stats={k:[] for k in shock_candidates}
    for fold in range(5):
        inner_train=[s for s in training_sessions if fold_of[s]!=fold]
        inner_test=[s for s in training_sessions if fold_of[s]==fold]
        assert len(inner_train)==16 and len(inner_test)==4
        model=fit([row for s in inner_train for group in by[s] for row in group],calibration_variant)
        for sid in inner_test:
            source=projected(by[sid],model)
            p=[x[0] for x in source]
            y=[x[1] for x in source]
            prev=[x[2] for x in source]
            for option in shock_candidates:
                family,tau=option
                losses=loglosses(p,y,prev,family,tau)
                stats[option].append(float(losses.mean()))
    mean={k:sum(values)/len(values) for k,values in stats.items()}
    best=min(shock_candidates,key=lambda x:(mean[x],x))
    return best, mean


def run(groups,*,draws=4000,seed=20261109,model_names=('frequency','selected')):
    if draws<1:raise ValueError('draws must be positive')
    score=evaluate(groups)
    actor_choices,_=trained_choices(score)
    events=event_rows(groups,actor_choices)
    by=defaultdict(list)
    for group in events:
        r=group[0];by[r['session'],r['treatment'],r['model']].append(group)
    sessions=sorted({key[0] for key in groups})
    if len(sessions)!=24:raise ValueError('need 24 original independent sessions')
    fold_of={s:i%6 for i,s in enumerate(sessions)}
    selections=[];observed=[]
    for fold in range(6):
        training=[s for s in sessions if fold_of[s]!=fold]
        testing=[s for s in sessions if fold_of[s]==fold]
        assert len(training)==20 and len(testing)==4
        for treatment in (1,2,3):
            for model_name in model_names:
                train_groups=[g for s in training for g in by[s,treatment,model_name]]
                calibration_variant,_=choose_calibration(train_groups,training)
                best,scores=training_shock_choice(train_groups,training,calibration_variant)
                calibration=fit([r for g in train_groups for r in g],calibration_variant)
                selections.append(dict(fold=fold,treatment=treatment,model=model_name,
                                       calibration=calibration_variant,shock_family=best[0],
                                       tau=best[1],train_sessions=20,test_sessions=4,
                                       inner_heldout_baseline=scores[('common',0.0)],
                                       inner_heldout_chosen=scores[best]))
                for session in testing:
                    groups_to_score=projected(by[session,treatment,model_name],calibration)
                    for ps,y,prev,_,period in groups_to_score:
                        base=forecast(ps).evaluate(y)
                        latent=forecast(ps,best[1],best[0],prev).evaluate(y)
                        observed.append(dict(session=session,treatment=treatment,
                                             model=model_name,period=period,
                                             baseline=base,latent=latent))
    if len(observed)!=len(groups)*len(model_names):
        raise ValueError('missing heldout groups')
    return summarize(observed,selections,sessions,draws=draws,seed=seed,groups=len(groups))


def summarize(rows,selections,sessions,*,draws=4000,seed=20261109,groups=5760):
    by=defaultdict(list)
    for r in rows:by[r['session'],r['treatment'],r['model']].append(r)
    comparisons=[]
    for treatment in (1,2,3):
        for model in sorted({r['model'] for r in rows}):
            session_rows=[by[s,treatment,model] for s in sessions]
            if any(len(g)==0 for g in session_rows):raise ValueError('missing session')
            metrics={}
            for name in METRICS:
                baseline=[sum(g['baseline'][name] for g in gr)/len(gr) for gr in session_rows]
                latent=[sum(g['latent'][name] for g in gr)/len(gr) for gr in session_rows]
                differences=[v-u for u,v in zip(baseline,latent)]
                rng=Random(seed+treatment+(0 if model=='frequency' else 100)+METRICS.index(name))
                intervals=sorted(sum(rng.choice(differences) for _ in sessions)/len(sessions)
                                 for _ in range(draws))
                metrics[name]=dict(baseline=sum(baseline)/len(sessions),
                                   latent=sum(latent)/len(sessions),
                                   delta=sum(differences)/len(sessions),
                                   interval95=[intervals[int(.025*draws)],intervals[int(.975*draws)]],
                                   better_sessions=sum(d<0 for d in differences))
            comparisons.append(dict(treatment=treatment,model=model,sessions=len(sessions),metrics=metrics))
    return dict(source_sessions=len(sessions),source_groups=groups,
                fold_plans=selections,comparisons=comparisons,
                caveat='Exploratory historical data reuse; latent binary shock is not identified group strategy. Tau selection only uses outer training sessions. Marginal actor probabilities fixed.')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('original_source')
    p.add_argument('--draws',type=int,default=4000)
    p.add_argument('--output',default='r26_source_aggregate.json')
    a=p.parse_args()
    result=run(load_groups(a.original_source),draws=a.draws)
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    for item in result['comparisons']:
        m=item['metrics']
        print('treatment',item['treatment'],'model',item['model'],
              'group_logloss_delta',round(m['logloss']['delta'],6),
              'joint_logloss_delta',round(m['joint_logloss']['delta'],6),
              'cost_mae_delta',round(m['cost_mae']['delta'],6),
              'actor_brier_delta',round(m['actor_brier']['delta'],9))
    print('chosen',[(x['treatment'],x['model'],x['shock_family'],x['tau']) for x in result['fold_plans']])

if __name__=='__main__':main()
