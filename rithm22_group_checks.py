#!/usr/bin/env python3
"""RITHM-2.2 optional micro-to-macro falsifier diagnostics, NO causal interpretation.

Run after rithm22_audit.py using its --out-dir output. One genuine cluster is
one interacting live group, NOT one individual or one group-period.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

def welfare(s):
    return -36+66*s-5*s*s

def analyze(folder, seed=2202026, boot=20000):
    pred=pd.read_csv(folder/'rithm22_predictions_alpha25.csv')
    round_data=pd.read_csv(folder/'rithm22_round_diagnostics.csv')
    assert len(pred)==17100 and len(round_data)==950
    rng=np.random.default_rng(seed)
    out={'version':'RITHM-2.2 independent audit', 'cluster_count':10,
         'caveats':['exploratory repeated ten-group reuse',
           'off-diagonal residual products can also reflect probability miscalibration',
           'mean prediction is NOT the MAE-optimal payoff point forecast',
           'recipient selection in treatment 3/4 is endogenous']}
    output=[];scores=[]
    for (session,period),grp in pred.groupby(['Session','Period'],sort=True):
        actual=int(grp['LaneS'].sum())
        g={'session':int(session),'period':int(period),'epoch':'post' if period>=51 else 'pre','s':actual,'welfare':float(welfare(actual))}
        for name,field in [('state','p_state'),('history','p_hist')]:
            p=grp[field].to_numpy();previous=grp['prev_lane'].to_numpy()
            q=np.where(previous==1,1-p,p)
            pmf=np.array([1.])
            for x in q:
                pmf=np.convolve(pmf,[1-x,x])
            assert len(pmf)==19 and abs(pmf.sum()-1)<1e-9
            svals=np.arange(19);cdf=np.cumsum(pmf)
            posterior_w=float(np.dot(welfare(svals),pmf))
            ma,mb=(previous==0),(previous==1)
            residual=grp['target'].to_numpy()-p
            eA=residual[ma].sum(); eB=residual[mb].sum()
            withinA=eA*eA-np.sum(residual[ma]**2)
            withinB=eB*eB-np.sum(residual[mb]**2)
            between=-2*eA*eB
            g[name+'_count_logscore']=-float(np.log(max(pmf[actual],1e-300)))
            g[name+'_count_crps']=float(np.sum((cdf[:-1]-(np.arange(18)>=actual))**2))
            g[name+'_cover90']=int(np.searchsorted(cdf,.05)<=actual<=np.searchsorted(cdf,.95))
            g[name+'_payoff_mse']=(posterior_w-welfare(actual))**2
            g[name+'_plugin_welfare_mae']=abs(float(welfare(q.sum()))-welfare(actual))
            g[name+'_withinA']=float(withinA);g[name+'_withinB']=float(withinB)
            g[name+'_between']=float(between);g[name+'_offdiag']=float(withinA+withinB+between)
        scores.append(g)
    scores=pd.DataFrame(scores)
    assert np.allclose(scores['history_offdiag'],round_data['offdiag_h'])
    assert np.allclose(scores['state_offdiag'],round_data['offdiag_s'])
    scores.to_csv(folder/'rithm22_group_scores.csv',index=False)
    out['score_means']={k:float(scores[k].mean()) for k in scores.columns if k.startswith(('history_','state_'))}
    out['by_epoch']={str(epoch):{k:float(g[k].mean()) for k in g.columns if k.startswith(('history_','state_'))} for epoch,g in scores.groupby('epoch')}
    out['bootstrap']={}
    for model,suffix in [('state','s'),('history','h')]:
        fields=[f'ind_v_{suffix}',f'resid_sq_{suffix}',f'offdiag_{suffix}',f'payoff_abs_{suffix}']
        sessionmeans=round_data.groupby('Session')[fields].mean().to_numpy()
        assert sessionmeans.shape==(10,4)
        ix=rng.integers(0,10,size=(boot,10))
        sampled=sessionmeans[ix].mean(axis=1)
        ratio=sampled[:,1]/sampled[:,0]
        out['bootstrap'][model]={
            'variance_ratio':float(sessionmeans[:,1].mean()/sessionmeans[:,0].mean()),
            'ratio_95_percentile':np.quantile(ratio,[.025,.975]).tolist(),
            'mean_offdiag':float(sessionmeans[:,2].mean()),
            'offdiag_95_percentile':np.quantile(sampled[:,2],[.025,.975]).tolist(),
            'by_group_offdiag':sessionmeans[:,2].tolist()}
    by_group=pred.groupby('Session')[['ll_state','ll_hist']].mean()
    by_round=round_data.groupby('Session')[['payoff_abs_s','payoff_abs_h']].mean()
    out['paired_gain_by_group']={
        'individual_logloss':(by_group.ll_state-by_group.ll_hist).tolist(),
        'expected_welfare_MAE':(by_round.payoff_abs_s-by_round.payoff_abs_h).tolist()}
    (folder/'rithm22_group_checks.json').write_text(json.dumps(out,indent=2))
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('audit_output_dir',type=Path)
    parser.add_argument('--seed',type=int,default=2202026)
    parser.add_argument('--bootstrap-draws',type=int,default=20000)
    args=parser.parse_args()
    result=analyze(args.audit_output_dir,args.seed,args.bootstrap_draws)
    print(json.dumps({'score_means':result['score_means'],'bootstrap':result['bootstrap']},indent=2))
