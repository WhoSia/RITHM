#!/usr/bin/env python3
"""RITHM-2.2 independent Study-1 micro-to-macro audit.

Runs locally on the exact author Study-1 CSV, no GitHub Actions or new data.
Exploratory leave-one-live-group-out evaluation: ten groups have been reused.
"""
from __future__ import annotations
import argparse, json, hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, xlogy

EXPECTED_COLS={'Period','Subject','Profit','LaneM','LaneS','S','M','Session','Treatment','switch','infotreat'}
LAMBDAS=(1e-4,1e-3,1e-2)
ALPHAS=(5.,25.,100.)
def welfare(s): return -36 + 66*s - 5*s*s

def load_cases(path):
    raw=Path(path).read_bytes()
    d=pd.read_csv(path)
    assert EXPECTED_COLS == set(d.columns)
    assert len(d)==18000 and d['Session'].nunique()==10
    assert len(d.groupby(['Session','Period']))==1000
    assert len(d.groupby(['Session','Subject']))==180
    assert d.groupby(['Session','Subject']).size().eq(100).all()
    assert d.groupby(['Session','Period']).size().eq(18).all()
    assert ((d['LaneS']+d['LaneM'])==1).all()
    assert ((d['S']+d['M'])==18).all()
    assert (d['Profit']==np.where(d['LaneS']==1,28-3*d['S'],-2+2*d['S'])).all()
    assert d.groupby(['Session','Period'])['LaneS'].sum().eq(d.groupby(['Session','Period'])['S'].first()).all()
    assert d['switch'].isna().sum()==180
    d=d.sort_values(['Session','Subject','Period']).reset_index(drop=True)
    group=d.groupby(['Session','Subject'],sort=False)
    d['prev_lane']=group['LaneS'].shift(1)
    d['prev_occupancy']=group['S'].shift(1)
    d['prev_payoff']=group['Profit'].shift(1)
    d['other_prev_payoff']=np.where(d['prev_lane']==1,-2+2*d['prev_occupancy'],28-3*d['prev_occupancy'])
    d['payoff_diff']=d['other_prev_payoff']-d['prev_payoff']
    d['actual_switch']=(d['LaneS']!=d['prev_lane']).astype(int)
    mask=d['Period']>1
    assert (d.loc[mask,'switch']==d.loc[mask,'actual_switch']).all()
    d['past_four_switches']=group['actual_switch'].transform(lambda v: v.shift(1).rolling(4,min_periods=4).sum())
    # ending at t-1: run-length of exactly the same road, capped at 15
    lane=d['LaneS'].to_numpy(); run=np.ones(len(d),dtype=int)
    for i in range(1,len(d)):
        if d.at[i,'Session']==d.at[i-1,'Session'] and d.at[i,'Subject']==d.at[i-1,'Subject'] and lane[i]==lane[i-1]:
            run[i]=run[i-1]+1
    d['prev_streak']=pd.Series(run,index=d.index).groupby([d['Session'],d['Subject']]).shift(1).clip(upper=15)
    d=d[d['Period']>=6].copy().reset_index(drop=True)
    assert len(d)==17100 and d.groupby(['Session','Period']).size().eq(18).all()
    d['epoch']=(d['Period']>=51).astype(int)
    d['prev_sign']=np.sign(d['payoff_diff']).astype(int)
    d['occ_bin']=(d['prev_occupancy']//3).astype(int)
    d['history_bin']=np.where(d['past_four_switches']==0,0,np.where(d['past_four_switches']<=2,1,2))
    # Historical reconstruction: lagged contrast is deterministic in previous road and occupancy.
    assert np.all(d['payoff_diff']==np.where(d['prev_lane']==1,5*d['prev_occupancy']-30,30-5*d['prev_occupancy']))
    cols=['prev_lane','occ_bin','prev_sign','epoch','infotreat']
    d['state_key']=list(map(tuple,d[cols].to_numpy(dtype=int)))
    d['history_key']=[(*a,int(b)) for a,b in zip(d['state_key'],d['history_bin'])]
    d['target']=d['actual_switch']
    return d,hashlib.sha256(raw).hexdigest()

def nonparametric(d,alpha):
    v=[]
    for ss in sorted(d['Session'].unique()):
        train=d.loc[d['Session']!=ss]; test=d.loc[d['Session']==ss].copy()
        globalrate=train['target'].mean()
        st=train.groupby('state_key')['target'].agg(['sum','count'])
        ht=train.groupby('history_key')['target'].agg(['sum','count'])
        state_prior={key:(r['sum']+alpha*globalrate)/(r['count']+alpha) for key,r in st.iterrows()}
        state_probs=np.array([state_prior.get(k,globalrate) for k in test['state_key']])
        history_counts={key:(int(row['sum']),int(row['count'])) for key,row in ht.iterrows()}
        history_probs=np.array([(history_counts[k][0]+alpha*state_prior.get(k[:5],globalrate))/(history_counts[k][1]+alpha) if k in history_counts else state_prior.get(k[:5],globalrate) for k in test['history_key']])
        # key missing state fallback needs appropriate smoothing even for unobserved history key
        test['p_state']=state_probs; test['p_hist']=history_probs
        v.append(test)
    pred=pd.concat(v,ignore_index=True)
    return pred

def grouped_audit(pred,pkey):
    q=np.where(pred['prev_lane'].to_numpy()==1,1-pred[pkey].to_numpy(),pred[pkey].to_numpy())
    t=pred[['Session','Treatment','Period','epoch','infotreat','LaneS','prev_lane','target']].copy()
    t['q']=q;t['v']=q*(1-q);t['resid']=t['LaneS']-t['q'];t['sq_resid']=t['resid']**2
    t['A_resid']=np.where(t['prev_lane']==0,t['target']-pred[pkey],0.)
    t['B_resid']=np.where(t['prev_lane']==1,t['target']-pred[pkey],0.)
    t['v_A']=np.where(t['prev_lane']==0,pred[pkey]*(1-pred[pkey]),0.)
    t['v_B']=np.where(t['prev_lane']==1,pred[pkey]*(1-pred[pkey]),0.)
    agg=t.groupby(['Session','Treatment','Period','epoch'],sort=True).agg(S=('LaneS','sum'),mu=('q','sum'),ind_v=('v','sum'),single_sq=('sq_resid','sum'),eA=('A_resid','sum'),eB=('B_resid','sum'),vA=('v_A','sum'),vB=('v_B','sum'),informed=('infotreat','sum')).reset_index()
    agg['resid']=agg['S']-agg['mu'];agg['resid_sq']=agg['resid']**2
    agg['offdiag']=agg['resid_sq']-agg['single_sq'];agg['AB_resid_product']=agg['eA']*agg['eB']
    agg['payoff_actual']=welfare(agg['S']);agg['payoff_pred']=welfare(agg['mu'])-5*agg['ind_v']
    agg['side_abs']=np.abs(agg['resid']);agg['payoff_abs']=np.abs(agg['payoff_pred']-agg['payoff_actual'])
    agg['payoff_signed']=agg['payoff_pred']-agg['payoff_actual']
    agg['mean_term']=(66-10*agg['mu'])*(agg['mu']-agg['S'])
    agg['variance_term']=5*(agg['resid_sq']-agg['ind_v'])
    assert np.max(np.abs(agg['mean_term']+agg['variance_term']-agg['payoff_signed']))<1e-8
    return agg

def overview(a):
    cols=['mu','S','ind_v','resid_sq','single_sq','offdiag','AB_resid_product','eA','eB','vA','vB','side_abs','payoff_abs','payoff_signed','mean_term','variance_term']
    return {c:float(a[c].mean()) for c in cols}|{'n_rounds':int(len(a)),'variance_ratio':float(a['resid_sq'].mean()/a['ind_v'].mean())}

def summarize_nonparam(d,outdir):
    results={}
    for alpha in ALPHAS:
        p=nonparametric(d,alpha)
        p['ll_state']=-(xlogy(p['target'],p['p_state'])+xlogy(1-p['target'],1-p['p_state']))
        p['ll_hist']=-(xlogy(p['target'],p['p_hist'])+xlogy(1-p['target'],1-p['p_hist']))
        per_fold=p.groupby('Session')[['ll_state','ll_hist']].mean();per_fold['gain']=per_fold['ll_state']-per_fold['ll_hist']
        stats={}
        for model,key in [('state','p_state'),('history','p_hist')]:
            a=grouped_audit(p,key)
            stats[model]={'overall':overview(a), 'by_epoch':{str(k):overview(z) for k,z in a.groupby('epoch')},'by_treatment':{str(k):overview(z) for k,z in a.groupby('Treatment')},'by_session':{str(k):overview(z) for k,z in a.groupby('Session')},'epoch_treatment':{f'{t}.{e}':overview(z) for (t,e),z in a.groupby(['Treatment','epoch'])}}
        results[str(alpha)]={'ll_state':float(per_fold['ll_state'].mean()),'ll_history':float(per_fold['ll_hist'].mean()),'gains_by_group':{str(k):float(v) for k,v in per_fold['gain'].items()},'macro':stats}
        if alpha==25:
            # Full group-level time series for reproducibility and downstream competing hypothesis tests.
            a0=grouped_audit(p,'p_state');a1=grouped_audit(p,'p_hist');
            a=a0.merge(a1,on=['Session','Treatment','Period','epoch','S','informed','payoff_actual'],suffixes=('_s','_h'))
            a.to_csv(outdir/'rithm22_round_diagnostics.csv',index=False)
            p.to_csv(outdir/'rithm22_predictions_alpha25.csv',index=False)
    return results

def make_matrix(d):
    # Numerical scaling fixed by experiment design, not fitted using group 10 test values.
    t=pd.get_dummies(d['Treatment'],prefix='arm',dtype=float)
    for name in ['arm_2','arm_3','arm_4']:
        if name not in t:t[name]=0.
    # 10 state features, 12 history features incl intercept
    state=np.column_stack((np.ones(len(d)),d['prev_lane'],d['prev_occupancy']/18,d['prev_payoff']/40,d['payoff_diff']/40,d['Period']/100,d['infotreat'],t[['arm_2','arm_3','arm_4']].to_numpy()))
    hist=np.column_stack((state,d['past_four_switches']/4,d['prev_streak']/15))
    assert state.shape==(17100,10) and hist.shape==(17100,12)
    return state,hist

def logistic_fit(X,y,lam,optimizer='lbfgs',epochs=110):
    n=len(y);mask=np.r_[0.,np.ones(X.shape[1]-1)]
    def fg(w):
        z=X@w
        loss=np.logaddexp(0,z).mean() - y@z/n +.5*lam*np.sum((w*mask)**2)
        grad=X.T@(expit(z)-y)/n+lam*w*mask
        return loss,grad
    if optimizer=='lbfgs':
        res=minimize(fg,np.zeros(X.shape[1]),jac=True,method='L-BFGS-B',options={'gtol':1e-10,'ftol':1e-13,'maxiter':2500,'maxls':30})
        return res.x,{'loss':float(res.fun),'grad_norm':float(np.linalg.norm(fg(res.x)[1])),'iterations':int(res.nit),'optimizer_success':bool(res.success),'optimizer_message':str(res.message)}
    w=np.zeros(X.shape[1]);m=np.zeros_like(w);v=np.zeros_like(w);lr=.05
    for k in range(1,epochs+1):
        _,grad=fg(w)
        m=.9*m+.1*grad; v=.999*v+.001*grad**2
        w-=lr*(m/(1-.9**k))/(np.sqrt(v/(1-.999**k))+1e-8)
    loss,grad=fg(w)
    return w,{'loss':float(loss),'grad_norm':float(np.linalg.norm(grad)),'iterations':epochs,'optimizer_success':None,'optimizer_message':'Adam lr=0.05 beta=(.9,.999) initialization zero, not necessarily original settings'}

def audit_logistic(d):
    Xs,Xh=make_matrix(d);y=d['target'].to_numpy(dtype=float);ss=d['Session'].to_numpy()
    outcome={}
    for lam in LAMBDAS:
        foldstats=[]
        for held in range(1,11):
            train=ss!=held;test=~train
            row={'session':held}
            for lab,X in [('state',Xs),('history',Xh)]:
                optimum,stat=logistic_fit(X[train],y[train],lam)
                adam110,early=logistic_fit(X[train],y[train],lam,'adam',110)
                adam400,late=logistic_fit(X[train],y[train],lam,'adam',400)
                def ll(w):
                    z=X[test]@w
                    return float(np.mean(np.logaddexp(0,z)-y[test]*z))
                row[lab]={'lbfgs':stat|{'test_logloss':ll(optimum)},'adam110':early|{'test_logloss':ll(adam110)},'adam400':late|{'test_logloss':ll(adam400)},'opt_train_loss_delta_110':early['loss']-stat['loss']}
            foldstats.append(row)
        outcome[str(lam)]={'per_fold':foldstats,'test_means':{f'{model}_{fit}':float(np.mean([r[model][fit]['test_logloss'] for r in foldstats])) for model in ['state','history'] for fit in ['lbfgs','adam110','adam400']},'avg_grad_norm_110':{m:float(np.mean([r[m]['adam110']['grad_norm'] for r in foldstats])) for m in ['state','history']},'avg_grad_norm_lbfgs':{m:float(np.mean([r[m]['lbfgs']['grad_norm'] for r in foldstats])) for m in ['state','history']},'max_loss_gap_110':{m:max(r[m]['opt_train_loss_delta_110'] for r in foldstats) for m in ['state','history']},'all_10_history_better_lbfgs':all(r['state']['lbfgs']['test_logloss']>r['history']['lbfgs']['test_logloss'] for r in foldstats)}
    return outcome

def main():
    ap=argparse.ArgumentParser();ap.add_argument('csv');ap.add_argument('--skip-logistic',action='store_true');ap.add_argument('--out-dir',type=Path,default=Path.cwd());args=ap.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    d,sha=load_cases(args.csv)
    out={'study':'RITHM-2.2 INDEPENDENT REIMPLEMENTATION','sha256':sha,'n_cases':len(d),'n_group_rounds':len(d.groupby(['Session','Period'])),'group_count':int(d['Session'].nunique()),'status':'EXPLORATORY_COURT_NOT_CAUSAL'}
    out['nonparam']=summarize_nonparam(d,args.out_dir)
    (args.out_dir/'rithm22_nonparam.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    if not args.skip_logistic:
        out['logistic']=audit_logistic(d)
    (args.out_dir/'rithm22_audit_results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    for a,res in out['nonparam'].items():
        st=res['macro']['state']['overall'];hi=res['macro']['history']['overall'];print('alpha',a,'individual_loss',res['ll_state'],res['ll_history'],'sideMAE',st['side_abs'],hi['side_abs'],'welfareMAE',st['payoff_abs'],hi['payoff_abs'],'history wins',sum(v>0 for v in res['gains_by_group'].values()))
    a=out['nonparam']['25.0']
    for kind in ['state','history']:
        print('alpha25',kind,'group distribution variance audit',json.dumps(a['macro'][kind]['overall'],indent=2))
    for lam,res in out.get('logistic',{}).items(): print('lambda',lam,'test_means',res['test_means'],'avg_grad_norm_110',res['avg_grad_norm_110'],'avg_grad_norm_lbfgs',res['avg_grad_norm_lbfgs'],'all10',res['all_10_history_better_lbfgs'])
    print('sha',sha)
if __name__=='__main__':main()
