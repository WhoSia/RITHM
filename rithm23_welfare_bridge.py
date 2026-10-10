#!/usr/bin/env python3
"""RITHM-2.3: exact cost-to-hysteresis bridge at the structural *accounting* level.

2017 Wijayaratna et al. human data, doi:10.1371/journal.pone.0184191.s002.
All component weights are published-network implied; route-cost cell anomalies
are preserved and never silently corrected. Running this is NO causal admission.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from rithm23_source_decode import decode
BASE=Path(__file__).resolve().parent

def predicted_path_cost(n1,n2,z,route):
    # Study network; n3=12-n1-n2.
    if route==1:return 10+n1+n2
    if route==2:return 13+n2+19*z
    if route==3:return 22-n1
    raise ValueError(route)

def predicted_social_cost(n1,n2,z):
    return 264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2

def read_model_rounds():
    df=decode()
    df['structural_cost']=[predicted_path_cost(*x) for x in zip(df.n1,df.n2,df.z,df.route)]
    df['individual_error']=df.cost-df.structural_cost
    assert (df.individual_error==0).sum()==5713 # 47 source individual inconsistencies.
    nonzero=df[df.individual_error!=0]
    key=['session','group','stage','t','info','z','n1','n2','n3']
    rnd=df.groupby(key,as_index=False).agg(realized=('cost','sum'),pred_individual_sum=('structural_cost','sum'),error_n=('individual_error',lambda x:int((x!=0).sum())))
    rnd['structural']=predicted_social_cost(rnd.n1,rnd.n2,rnd.z)
    rnd['delta']=rnd.realized-rnd.structural
    assert len(rnd)==480
    assert (abs(rnd.pred_individual_sum-rnd.structural)<1e-10).all()
    bad=rnd[rnd.error_n>0]
    assert len(bad)==6
    return df,rnd,bad

def decomp(frame):
    n1=frame.n1.to_numpy(dtype=float)
    n2=frame.n2.to_numpy(dtype=float)
    n3=frame.n3.to_numpy(dtype=float)
    z=frame.z.to_numpy(dtype=float)
    m1=float(n1.mean());m2=float(n2.mean());mz=float(z.mean())
    v1=float(n1.var());v3=float(n3.var());shockcov=float(np.mean((z-mz)*(n2-m2)))
    flowbase=predicted_social_cost(m1,m2,mz)
    dispersion=v1+v3
    shock=19*shockcov
    total=flowbase+dispersion+shock
    assert abs(total-frame.structural.mean())<1e-9, (total,frame.structural.mean())
    return dict(rounds=len(frame),mean_n1=m1,mean_n2=m2,mean_n3=float(n3.mean()),incident_rate=mz,
       base_mean_flow=float(flowbase),variance_n1=v1,variance_n3=v3,network_dispersion=float(dispersion),
       shock_route2_cov=shockcov,shock_response_term=float(shock),total_structural_cost=float(total),
       total_source_recorded_cost=float(frame.realized.mean()),source_difference=float((frame.realized-frame.structural).mean()))

def contrast(a,b):
    # info vs no-info as b-a, no causality claim.
    ka=['base_mean_flow','network_dispersion','shock_response_term','total_structural_cost','total_source_recorded_cost','source_difference']
    ans={k:float(b[k]-a[k]) for k in ka}
    assert abs(sum(ans[k] for k in ka[:3])-ans['total_structural_cost']) <1e-8
    return ans

def variance_couplings():
    # exact 12-person route 1 vs route 3 choices, all p_i=.5 each; E N1=6.
    # balanced N1=6; independent N1~Binomial(12,.5) v=3; comonotone N1=0 or12, v=36.
    r=[]
    for label,v in [('balanced',0),('independent',3),('comonotone',36)]:
        base=predicted_social_cost(6,0,0)
        # N3=12-N1 -> Var(N3)=Var(N1)=v
        value=base+2*v
        r.append(dict(law=label,p_each_route1=.5,mean_n1=6.0,variance_n1=v,
                      expected_system_cost=float(value),variance_penalty=2*v))
    return r

def main():
    df,rnd,bad=read_model_rounds()
    by_treat={str(x):decomp(g) for x,g in rnd.groupby('info')}
    across=contrast(by_treat['0'],by_treat['1'])
    session=[];paired=[]
    for sid,g in rnd.groupby('session'):
        d={str(tr):decomp(p) for tr,p in g.groupby('info')}
        session.append(dict(session=sid,noinfo=d['0'],info=d['1'],info_minus_noinfo=contrast(d['0'],d['1'])))
    for (sid,group),g in rnd.groupby(['session','group']):
        d={str(tr):decomp(p) for tr,p in g.groupby('info')}
        paired.append(dict(session=sid,group=int(group),info_minus_noinfo=contrast(d['0'],d['1'])))
    # leave each of the six sources out for stability (does not create independent confirmation).
    influence=[]
    for s in sorted(rnd.session.unique()):
        g=rnd[rnd.session!=s]
        d={str(tr):decomp(p) for tr,p in g.groupby('info')}
        influence.append(dict(removed=s,difference=contrast(d['0'],d['1'])))
    res={'article_doi':'10.1371/journal.pone.0184191','source_appendix_doi':'10.1371/journal.pone.0184191.s002',
         'n_original_records':len(df),'n_group_rounds':len(rnd),'n_exact_source_person_costs':int((df.individual_error==0).sum()),
         'n_nonmatching_source_person_costs':int((df.individual_error!=0).sum()),'n_nonmatching_source_group_rounds':len(bad),
         'anomaly_rounds':bad[['session','group','stage','t','info','z','n1','n2','n3','realized','structural','delta','error_n']].to_dict('records'),
         'derivation':'cost_r: route1=10+n1+n2; route2=13+n2+19z; route3=22-n1; C=264-24n1-9n2+2n1²+2n1*n2+n2²+19z*n2',
         'exact_identity':'E[C]=C(E[n1],E[n2],E[z])+Var(n1)+Var(n3)+19Cov(z,n2), n3=12-n1-n2',
         'pooled_per_treatment':by_treat,'contrast_info_minus_noinfo':across,'six_session_contrasts':session,
         'paired_group_contrasts':paired,'leave_one_session_influence':influence,
         'fixed_person_marginal_exact_witness':variance_couplings(),
         'scientific_interpretation':'Exact accounting for the stated network, not causal information effect or a new theorem. Real source cost may mismatch structural cost in six rounds; both retained.'}
    out=BASE/'rithm23_exact_bridge_results.json'
    out.write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
    rnd.to_csv(BASE/'rithm23_exact_bridge_rounds.csv',index=False)
    print(json.dumps({k:v for k,v in res.items() if k in ('n_original_records','n_group_rounds','n_exact_source_person_costs','n_nonmatching_source_person_costs','n_nonmatching_source_group_rounds','anomaly_rounds','pooled_per_treatment','contrast_info_minus_noinfo','fixed_person_marginal_exact_witness')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
