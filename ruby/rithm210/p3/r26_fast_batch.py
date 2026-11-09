"""NumPy-only vectorized evaluation of unchanged R26 latent occupancy law."""
import numpy as np
from r26_common_shock import forecast


def _poisson_binomial_batch(probs):
    n=probs.shape[0]
    state=np.zeros((n,7),dtype=np.float64)
    state[:,0]=1.
    for i in range(6):
        p=probs[:,i]
        state[:,1:i+2]=state[:,1:i+2]*(1-p[:,None])+state[:,:i+1]*p[:,None]
        state[:,0]*=(1-p)
    return state


def loglosses(ps,ys,prev,family,tau):
    ps=np.asarray(ps,dtype=float)
    ys=np.asarray(ys,dtype=int)
    prev=np.asarray(prev,dtype=int)
    if ps.ndim!=2 or ps.shape[1]!=6 or ys.shape!=ps.shape or prev.shape!=ps.shape:
        raise ValueError('batch requires Nx6 groups')
    if not np.isfinite(ps).all() or (ps<0).any() or (ps>1).any():raise ValueError('invalid p')
    if not np.isin(prev,[-1,0,1]).all():raise ValueError('previous route')
    if not np.isin(ys,[0,1]).all():raise ValueError('binary outcome')
    if family=='common':sign=np.ones_like(ps)
    elif family=='previous_route_signed':sign=np.where(prev==-1,0,np.where(prev==1,1,-1))
    else:raise ValueError('invalid family')
    shift=tau*sign*np.minimum(ps,1-ps)
    plus=ps+shift;minus=ps-shift
    a=_poisson_binomial_batch(plus)
    b=_poisson_binomial_batch(minus)
    mass=(a+b)*0.5
    return -np.log(np.maximum(mass[np.arange(ps.shape[0]),ys.sum(axis=1)],1e-300))
