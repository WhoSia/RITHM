"""Private-author ZIP -> public aggregate-only original-session uncertainty audit.

Must pass original approved SHA gate in r65_endogenous_stability.load_private.
Original participant ZIP, actor IDs, per-group/session/period traces NEVER emitted.
"""
import argparse,json
from collections import Counter,defaultdict
from fractions import Fraction as F
from math import comb
from pathlib import Path
from random import Random
from r65_endogenous_stability import load_private,transition_event,TREATMENT,APPROVED_SHA
from r66_t8_cluster_bounds import ratio_interval
from r66_t8_moment_polytope import sharp_interval,verify_certificate
from r66_t8_welfare import recovery_excess,stage_excess
EPOCHS={'early':range(1,11),'late':range(30,40)}

def aggregate_private(groups,*,draws=600,seed=20261121):
    ses=defaultdict(Counter)
    sessions=sorted({s for s,_,_ in groups})
    if len(sessions)!=24:raise ValueError('24 whole sessions expected')
    for (sid,g,trt),hist in groups.items():
        for ep,ts in EPOCHS.items():
            for t in ts:
                v=transition_event(hist[t],hist[t+1])
                if v['a_before']!=4:continue
                k=v['down']
                ses[sid,trt,ep].update({'N':1,f'K{k}':1,'Ksum':k,
                    'choose2':comb(k,2),'choose3':comb(k,3),
                    'recovery':int(recovery_excess(k)),
                    'stage':int(stage_excess(k))})
    rng=Random(seed)
    out={}
    for trt,title in TREATMENT.items():
        out[title]={}
        for ep in EPOCHS:
            counts=[ses[sid,trt,ep] for sid in sessions]
            pooled=Counter()
            for c in counts:pooled.update(c)
            n=pooled['N']
            if n<100:raise ValueError('source cell <100 opportunities')
            observed_m1=F(pooled['Ksum'],4*n)
            observed_m2=F(pooled['choose2'],6*n)
            observed_m3=F(pooled['choose3'],4*n)
            obj=[recovery_excess(k) for k in range(5)]
            bounds={1:(observed_m1,observed_m1),2:(observed_m2,observed_m2)}
            sharp=sharp_interval(obj,bounds)
            assert verify_certificate(sharp,obj,bounds)
            fee=F(pooled['recovery'],n)
            if not sharp.lower<=fee<=sharp.upper:raise AssertionError('empirical law outside hull')
            den=[c['N'] for c in counts]
            union_bounds={}
            for d,factor,numkey in [(1,4,'Ksum'),(2,6,'choose2')]:
                num=[F(c[numkey],factor) for c in counts]
                lower,upper,rad=ratio_interval(num,den,bmax=20,num_moments=2)
                union_bounds[d]=(lower,upper)
            worst=sharp_interval(obj,union_bounds)
            boot=[]
            for _ in range(draws):
                selected=[counts[rng.randrange(24)] for _ in sessions]
                nn=sum(c['N'] for c in selected)
                if nn<=0:continue
                boot.append(sum(c['recovery'] for c in selected)/nn)
            boot.sort()
            def dec(x):return round(float(x),6)
            out[title][ep]={
                'old_A4_opportunities':n,
                'K_distribution':{str(i):pooled[f'K{i}'] for i in range(5)},
                'moments':{'actor_averaged_flip':dec(observed_m1),
                    'pair_averaged_coswitch':dec(observed_m2),
                    'triple_averaged_coswitch':dec(observed_m3)},
                'observed_stylized_recovery_excess':dec(fee),
                'point_marginal_pair_identification_interval':[dec(sharp.lower),dec(sharp.upper)],
                'point_id_interval_exact_fraction':[str(sharp.lower),str(sharp.upper)],
                'point_id_width':dec(sharp.upper-sharp.lower),
                'cluster_hoeffding_95_simultaneous_moment_intervals':{f'm{d}':[dec(lo),dec(hi)] for d,(lo,hi) in union_bounds.items()},
                'sampling_plus_identification_robust_interval':[dec(worst.lower),dec(worst.upper)],
                'whole_session_bootstrap_descriptive_recovery_95':[
                    dec(boot[int(.025*len(boot))]),
                    dec(boot[min(len(boot)-1,int(.975*len(boot)))]] if boot else None,
                'uncertainty_unit':'24 original sessions, NOT 100s of independent periods'}
    return {'source_sha256_validated':APPROVED_SHA,
        'status':'EXPLORATORY_SAME_24_SESSION_COHORT_NOT_CAUSAL',
        'stochastic_model':'K=0..4 A->B moves and hypothetical one-per-period recovery; group state only analyst filter',
        'model_uncertainty':'m1,m2 pinned or uncertain via 24-session Hoeffding union',
        'cluster_assumption':'IID 24 original sessions conditional for union Hoeffding coverage',
        'uncertainty_warning':'Hoeffding wide, descriptive bootstrap not independent confirmation',
        'bootstrap_resamples':draws,'pooled_by_treatment_epoch':out,
        'private_rows_exported':False}

def run(source,draws=600):
    return aggregate_private(load_private(source),draws=draws)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('source_zip')
    p.add_argument('aggregate_output_json')
    p.add_argument('--draws',type=int,default=600)
    a=p.parse_args()
    result=run(a.source_zip,draws=a.draws)
    Path(a.aggregate_output_json).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:{ep:v['old_A4_opportunities'] for ep,v in cs.items()} for k,cs in result['pooled_by_treatment_epoch'].items()}))
if __name__=='__main__':main()
