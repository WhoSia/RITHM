# Python 3 + NumPy. Private source CSV remains local; public output aggregates only.
# R22: FFT speeds up the SAME with-replacement SSM rule, not exact arithmetic.
import csv, hashlib, json, math, sys
from collections import defaultdict
from decimal import Decimal
import numpy as np

SHA = 'd36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
COST = np.array([n*n + 2*(6-n)**2 for n in range(7)])

def sampled_q_probabilities(pool, qmax=9):
    if not len(pool): return np.full(qmax, 0.5)
    pool=np.asarray(pool,dtype=np.int64)
    bottom=int(pool.min()); top=int(pool.max())
    hist=np.bincount(pool-bottom,minlength=top-bottom+1).astype(np.float64)
    hist/=len(pool)
    fft_size=1 << (qmax*(top-bottom)).bit_length()
    spectrum=np.fft.rfft(hist,n=fft_size)
    powers=spectrum[None,:] ** np.arange(1,qmax+1)[:,None]
    coefficients=np.fft.irfft(powers,n=fft_size,axis=1)
    answers=[]
    for q in range(1,qmax+1):
        vals=coefficients[q-1,:q*(top-bottom)+1]
        zero=-q*bottom
        if zero<0: p=1.
        elif zero>=len(vals): p=0.
        else: p=float(vals[zero+1:].sum()+vals[zero]*0.5)
        answers.append(min(1.0,max(0.0,p)))
    return np.asarray(answers)

def run(path):
    with open(path,'rb') as handle:
        if hashlib.sha256(handle.read()).hexdigest()!=SHA:
            raise ValueError('Original CSV SHA-256 mismatch')
    groups=defaultdict(list)
    for row in csv.DictReader(open(path)):
        s=int(row['session']); trt=int(row['trt']); t=int(row['Period'])
        if s in (2,101) or trt not in (1,2,3) or not 1<=t<=40:continue
        groups[(s,int(row['section']),t,int(row['Group']))].append(row)
    if len(groups)!=5760 or not all(len(v)==6 for v in groups.values()):
        raise ValueError('Expected 5760 complete six-actor groups')
    states={}; stats=defaultdict(lambda:dict(n=0,logloss=0.,brier=0.,cost_abs_error=0.,cost_bias=0.))
    for s,section,t,g in sorted(groups):
        players=sorted(groups[(s,section,t,g)],key=lambda r:int(r['ID']))
        if len(set(int(r['ID']) for r in players))!=6:raise ValueError('Repeated actor')
        n=sum(int(r['RouteA']) for r in players)
        if not all(int(r['NumA'])==n for r in players):raise ValueError('Group state mismatch')
        treatment=int(players[0]['trt'])
        p_by_model={key:[] for key in ('frequency','persistent_q3','uniform_q3','persistent_q9','uniform_q9')}
        updates=[]
        for row in players:
            key=(s,section,int(row['ID']))
            if key not in states:
                states[key]=dict(period=0,a=0,pa=[],pb=[],diff=[],
                    weights3=np.full(3,1./3),weights9=np.full(9,1./9))
            state=states[key]
            if state['period']!=t-1:raise ValueError('Prior history continuity')
            informed=row['Informed']=='1'
            choice=int(row['RouteA'])
            if choice not in (0,1):raise ValueError('Nonbinary choice')
            if informed: candidate=sampled_q_probabilities(state['diff'])
            elif state['pa'] and state['pb']:
                differences=np.subtract.outer(np.asarray(state['pa'],dtype=np.int64),
                    np.asarray(state['pb'],dtype=np.int64)).ravel()
                candidate=sampled_q_probabilities(differences)
            else:candidate=np.full(9,.5)
            likelihood=candidate*.98+.01 # lapse .02, fair coin noise
            for size in (3,9):
                p_by_model['persistent_q'+str(size)].append(
                    float(np.dot(state['weights'+str(size)],likelihood[:size])))
                p_by_model['uniform_q'+str(size)].append(float(likelihood[:size].mean()))
            p_by_model['frequency'].append((state['a']+1)/(state['period']+2))
            updates.append((row,state,informed,choice,likelihood))
        for model,ps in p_by_model.items():
            distribution=np.array([1.])
            for p in ps:distribution=np.convolve(distribution,[1-p,p])
            predicted=float(distribution@COST); observed=float(COST[n])
            score=stats[(s,treatment,model)]
            score['n']+=1
            score['logloss']-=math.log(max(float(distribution[n]),sys.float_info.min))
            score['brier']+=float(np.sum((distribution-np.eye(7)[n])**2))
            score['cost_abs_error']+=abs(predicted-observed)
            score['cost_bias']+=predicted-observed
        for row,state,informed,choice,likelihood in updates:
            for size in (3,9):
                index='weights'+str(size)
                w=state[index]*(likelihood[:size] if choice else (1-likelihood[:size]))
                if w.sum()<=0:raise ValueError('Posterior zero support')
                state[index]=w/w.sum()
            payoff=int(Decimal(row['profit'])*10)
            if informed:
                other=n-(1 if choice else 0)
                if not 0<=other<=5:raise ValueError('Invalid group occupancy')
                state['diff'].append(10*(11-3*other))
            else:state['pa' if choice else 'pb'].append(payoff)
            state['period']+=1;state['a']+=choice
    aggregate=defaultdict(list); sessions=[]
    for (s,t,model),score in stats.items():
        rec=dict(session=s,treatment=t,model=model,groups=score['n'],
            **{metric:score[metric]/score['n'] for metric in
                ('logloss','brier','cost_abs_error','cost_bias')})
        sessions.append(rec)
        aggregate[(t,model)].append((s,score))
    models=[]
    for (trt,model),items in sorted(aggregate.items()):
        n=sum(st['n'] for _,st in items)
        models.append(dict(treatment=trt,model=model,groups=n,
            **{metric:sum(st[metric] for _,st in items)/n for metric in
                ('logloss','brier','cost_abs_error','cost_bias')}))
    return dict(groups=len(groups),sessions=24,models=models,
        session_results=sessions,
        warning='Repeated original historical data, original author latent-q fit not claimed; FFT double arithmetic, no causal inference.')

if __name__=='__main__':
    result=run(sys.argv[1])
    with open(sys.argv[2] if len(sys.argv)>2 else 'r22_q9_cv.json','w') as f:
        json.dump(result,f,indent=2)
    for row in result['models']:
        print(row['treatment'],row['model'],round(row['logloss'],6))
