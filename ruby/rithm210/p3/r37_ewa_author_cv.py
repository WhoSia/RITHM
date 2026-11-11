"""RITHM R37: original-author Appendix-A EWA-lite conditional forecast replay.

Author eqs (1)-(3), Appendix A.2 uniform inference, N0=1 and A_A0=A_B0=1.
Per-person posterior for unobserved other-A count uses all feasible 0..5
values with realized payoff + chosen-route cost within [6,16] under a
uniform *belief* over 6 possible profiles. This matches manuscript tables
10/11 for interval boundaries, modulo floating arithmetic.
Train lambda>=0 by training sessions only; score held-out six-choice and
occupancy likelihoods using same 24 main Partial sessions as RITHM R33.
No current observed Value/Cost or future choice is a predictor for uninformed.
"""
from __future__ import annotations
import json,sys
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize_scalar
from r37_ssm_source_cv import source_groups,group_metrics,SOURCE_SHA


def inferred_payoffs(y,profit,n=None):
    """Return proxy distribution of other-route A count k (0..5), foregone payoff.

    Informed provided n; uninformed sees only payoff. k plausibility from
    unobserved Value=P+Cost_y(k) in [6,16]. Chosen-route payoffs unchanged.
    """
    k=np.arange(6)
    if y==1:
        actualcost=k+1
        foregonecost=2*(6-k)
    elif y==0:
        actualcost=2*(6-k)
        foregonecost=k+1
    else:raise ValueError('binary route')
    if n is not None:
        other=int(n-y)
        if other not in k:raise ValueError('impossible true occupancy')
        probs=np.zeros(6);probs[other]=1.
    else:
        feasible=(profit+actualcost>=6-1e-9)&(profit+actualcost<=16+1e-9)
        if not feasible.any():raise ValueError('payoff violates possible Value range')
        probs=feasible.astype(float);probs/=sum(probs)
    foregone=profit+float(probs@(actualcost-foregonecost))
    return probs,foregone


def attractions(groups):
    """Returns for each session 6-person group arrays (diff attraction, actual y)."""
    out={}
    for sid,sec,g,actors,periods in groups:
        # A: attraction for A/B, Nx: accumulated experience, history of 6
        # possible 'other people choosing A' belief distributions.
        states={aid:{'A':np.array([1.,1.]),'N':1.,'hist':np.zeros(6)} for aid in actors}
        diffs=[];choices=[]
        for t in range(1,41):
            period_d=[];period_y=[]
            for aid in actors:
                state=states[aid];y,info,payoff,n=periods[t][aid]
                period_d.append(float(state['A'][1]-state['A'][0]));period_y.append(y)
                r,foregone=inferred_payoffs(y,payoff,n if info else None)
                prev_hist=state['hist']
                new_hist=(prev_hist*(t-1)+r)/t
                surprise=float(np.dot(new_hist-r,new_hist-r))
                phi=float(np.clip(1-.5*surprise,0,1))
                oldN=state['N'];newN=phi*oldN+1
                # Actual chosen action reinforced; unchosen iff expected foregone >= actual.
                feedback=np.array([foregone,foregone])
                feedback[y]=payoff
                delta=np.array([float(foregone>=payoff),float(foregone>=payoff)])
                delta[y]=1.
                state['A']=(phi*oldN*state['A']+delta*feedback)/newN
                state['N']=newN;state['hist']=new_hist
            if t>=2:
                diffs.append(period_d);choices.append(period_y)
        out.setdefault(sid,[]).extend(zip(diffs,choices))
    return out


def losses_at_lambda(rows,lmbda):
    X,Y=rows
    p=expit(lmbda*X)
    return float(np.mean(np.logaddexp(0,lmbda*X)-Y*(lmbda*X)))


def run(path):
    records=attractions(source_groups(path));sessions=sorted(records)
    feats={s:(np.asarray([a for a,y in records[s]]).reshape(-1),
              np.asarray([y for a,y in records[s]]).reshape(-1)) for s in sessions}
    folds={s:i%6 for i,s in enumerate(sessions)}
    held={};selected=[]
    for f in range(6):
        train=[s for s in sessions if folds[s]!=f]
        test=[s for s in sessions if folds[s]==f]
        if len(train)!=20 or len(test)!=4:raise ValueError('session fold contract')
        xs=np.concatenate([feats[s][0] for s in train]);ys=np.concatenate([feats[s][1] for s in train])
        def loss(l):return losses_at_lambda((xs,ys),l)
        fit=minimize_scalar(loss,bounds=(0,16),method='bounded',options={'xatol':1e-8})
        if not fit.success:raise ArithmeticError('lambda fit failed')
        lam=float(fit.x);selected.append({'fold':f,'lambda':lam,'training_actor_logloss':fit.fun})
        for sid in test:
            xs,ys=feats[sid];p=expit(lam*xs).reshape(-1,6);y=ys.reshape(-1,6)
            held[sid]=np.mean([group_metrics(x,v) for x,v in zip(p,y)],axis=0)
    return {'source_sha256':SOURCE_SHA,'sessions':len(sessions),'groups':48,'group_periods':1872,
       'model':'original-author Appendix-A EWA-lite, uniform-belief uninformed, lambda per fold train session MLE (0..16)',
       'metrics':['actor_logloss','independent_joint_logloss','occupancy_logloss','cost_MAE'],
       'heldout_session_equal_mean':np.mean([held[s] for s in sessions],axis=0).tolist(),
       'lambda_selected':selected,
       'limitations':['The original author Table 10/11 inferential payoffs and attention are implemented from text; boundary behavior verified on examples but complete author-source code is unavailable',
                      'Teacher-forced original action histories differ from unconditional EWA simulation',
                      'Fitting lambda on 20 training sessions prevents leakage to four heldout sessions',
                      'No psychological causality and no agent actually observed their hidden Value']}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r37_ewa_author_cv.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
