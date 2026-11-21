"""R66-T11 source-free guard: serial covariance decomposition is NOT a scoring rule.

The fully private 24-session LOSO analysis lives in approved source-free
Drive ZIP, never in this file. This is an independent mathematical witness.
"""
from fractions import Fraction as Q

def covariance(xs,ys):
    if len(xs)!=len(ys) or not xs:raise ValueError('matched non-empty samples')
    x=list(map(Q,xs));y=list(map(Q,ys));n=len(x)
    mx=sum(x,Q(0))/n;my=sum(y,Q(0))/n
    return sum(((a-mx)*(b-my) for a,b in zip(x,y)),Q(0))/n

def mse(y,pred):
    if len(y)!=len(pred) or not y:raise ValueError('matched non-empty samples')
    return sum(((Q(a)-Q(b))**2 for a,b in zip(y,pred)),Q(0))/len(y)

def decomposition(prior_delta,next_delta,forecast):
    if len(prior_delta)!=len(next_delta) or len(next_delta)!=len(forecast):
        raise ValueError('matched original transitions')
    residual=[Q(y)-Q(f) for y,f in zip(next_delta,forecast)]
    lhs=covariance(prior_delta,next_delta)
    model=covariance(prior_delta,forecast)
    remain=covariance(prior_delta,residual)
    assert lhs==model+remain
    return {'raw':lhs,'fitted':model,'residual':remain,'mse':mse(next_delta,forecast)}

def source_free_witness():
    x=[-1,1,-1,1]
    y=[-1,1,-1,1]
    good=decomposition(x,y,y)
    bad=decomposition(x,y,[0,0,0,0])
    assert good['residual']==0 and good['mse']==0
    assert bad['residual']!=0 and bad['mse']>0
    # Smaller serial residual covariance could coexist with higher MSE
    # when errors have a component orthogonal to prior changes.
    forecast=[-2,2,-2,2]
    overfit=decomposition(x,y,forecast)
    assert overfit['mse']>good['mse']
    return good,bad,overfit

if __name__=='__main__':print(source_free_witness())
