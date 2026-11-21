"""RITHM T10: exact Markov occupancy null for lagged observed revisions.

Not a claim that original human actors are Markov or independent.
"""
from fractions import Fraction as Q
from math import comb
N=6

def row_independent(n, flip_a, flip_b):
    if not isinstance(n,int) or not 0<=n<=N:raise ValueError('occupancy 0..6')
    p,q=Q(flip_a),Q(flip_b)
    if not 0<=p<=1 or not 0<=q<=1:raise ValueError('probabilities')
    ans=[Q(0)]*7
    for down in range(n+1):
        for up in range(7-n):
            pr=Q(comb(n,down)*comb(6-n,up))*p**down*(1-p)**(n-down)*q**up*(1-q)**(6-n-up)
            ans[n-down+up]+=pr
    assert sum(ans)==1
    return tuple(ans)

def transition(pa,pb):
    if len(pa)!=7 or len(pb)!=7:raise ValueError('seven rates')
    return tuple(row_independent(n,pa[n],pb[n]) for n in range(7))

def validate(P,pi):
    if len(P)!=7 or len(pi)!=7 or any(len(row)!=7 for row in P):raise ValueError('seven states')
    P=tuple(tuple(Q(x) for x in row) for row in P);pi=tuple(Q(x) for x in pi)
    if any(x<0 for row in P for x in row) or any(x<0 for x in pi) or any(sum(row)!=1 for row in P) or sum(pi)!=1:
        raise ValueError('probability law')
    return P,pi

def joint_moments(P,pi):
    P,pi=validate(P,pi)
    f=tuple(sum((P[j][k]*(k-j) for k in range(7)),Q(0)) for j in range(7))
    e0=sum((pi[i]*P[i][j]*(j-i) for i in range(7) for j in range(7)),Q(0))
    e1=sum((pi[i]*P[i][j]*f[j] for i in range(7) for j in range(7)),Q(0))
    raw=sum((pi[i]*P[i][j]*(j-i)*f[j] for i in range(7) for j in range(7)),Q(0))
    return {'lag_covariance':raw-e0*e1,'predicted_delta_given_next':f,
            'mean_first_delta':e0,'mean_second_delta':e1,
            'lag_covariance_of_next_innovation':Q(0)}

def binomial_occupancy_law(p):
    p=Q(p)
    if not 0<=p<=1:raise ValueError('p')
    return tuple(Q(comb(6,k))*p**k*(1-p)**(6-k) for k in range(7))

def independent_occupancy_null(p=Q(2,3)):
    pi=binomial_occupancy_law(p)
    return joint_moments(tuple(pi for _ in range(7)),pi)

if __name__=='__main__':
    assert independent_occupancy_null()['lag_covariance']==-Q(4,3)
    print('i.i.d. occupancy lag covariance:',independent_occupancy_null()['lag_covariance'])
