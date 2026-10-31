"""Posterior predictive for one participant with fixed q in {1,...,9}.
Uses only q-conditional choice probabilities calculated from previous feedback.
Not an identity-level latent q across independently reset treatment blocks.
"""
import numpy as np
from scipy.special import logsumexp

def predict_sequence(q_prob_A, chosen_A, lapse=0.0):
    q_prob_A=np.asarray(q_prob_A,float)
    chosen_A=np.asarray(chosen_A,int)
    if q_prob_A.ndim!=2 or q_prob_A.shape[1]!=9:raise ValueError("shape T x 9")
    if len(chosen_A)!=len(q_prob_A):raise ValueError("length mismatch")
    if not (0<=lapse<1):raise ValueError("lapse")
    logw=np.full(9,-np.log(9.0))
    forecasts=[]
    for p,y in zip(q_prob_A,chosen_A):
        if y not in (0,1):raise ValueError("choice")
        pp=np.clip((1-lapse)*p+lapse*.5,1e-12,1-1e-12)
        w=np.exp(logw-logsumexp(logw))
        forecasts.append(float(w@pp))
        logw+=np.log(pp if y else 1-pp)
        logw-=logsumexp(logw)
    return np.asarray(forecasts)
