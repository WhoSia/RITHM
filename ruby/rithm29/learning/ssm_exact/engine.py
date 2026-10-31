"""Exact finite-grid sample means; only previous-route payoff memories permitted."""
import numpy as np
from scipy.signal import fftconvolve
def distribution(values):
    z=np.asarray(values,float)*10
    if not np.allclose(z,np.rint(z),atol=1e-7): raise ValueError("payoff not on tenth grid")
    z=np.rint(z).astype(int); h=np.bincount(z-z.min()).astype(float)
    return int(z.min()),h/h.sum()
def exact_probabilities(a,b,max_q=9):
    if len(a)==0 or len(b)==0:return np.full(max_q,.5)
    amin,ah=distribution(a);bmin,bh=distribution(b)
    da=np.array([1.]);db=np.array([1.]);ans=[]
    for q in range(1,max_q+1):
        da=np.maximum(0,fftconvolve(da,ah));da/=da.sum()
        db=np.maximum(0,fftconvolve(db,bh));db/=db.sum()
        idx=q*(amin-bmin)+np.arange(len(da))
        cdf=np.r_[0.,np.cumsum(db)]
        below=cdf[np.clip(idx,0,len(db))]
        ties=np.zeros(len(da));valid=(idx>=0)&(idx<len(db));ties[valid]=db[idx[valid]]
        ans.append(float(np.clip(da@(below+.5*ties),0,1)))
    return np.array(ans)
