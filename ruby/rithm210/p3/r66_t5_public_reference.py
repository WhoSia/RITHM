"""R66-T5 minimal exact public reference. No real participant data.
Original experimental cost c_A(n)=n and c_B(6-n)=2*(6-n).
Behavioral switching rates are hypothetical, not estimated from humans.
"""
from fractions import Fraction as Q
from math import comb


def cost(n):
    if not isinstance(n,int) or n<0 or n>6:raise ValueError('occupancy')
    return 3*(n-4)**2


def rates(n):
    cost(n)
    return (Q(2,5) if 3*n-14>0 else Q(1,50),
            Q(2,5) if 11-3*n>0 else Q(1,50))


def row(n,p,q):
    """Exact occupancy transition and expected number of flips in one step."""
    prob=[Q(0)]*7;gross=Q(0)
    for d in range(n+1):
        pd=comb(n,d)*p**d*(1-p)**(n-d)
        for u in range(7-n):
            b=pd*comb(6-n,u)*q**u*(1-q)**(6-n-u)
            prob[n-d+u]+=b;gross+=b*(d+u)
    assert sum(prob)==1
    return tuple(prob),gross


def transition(clock=False,effort=Q(1),theta=Q(1,2)):
    """Two models have the same individual marginal revisions by previous n."""
    effort,theta=Q(effort),Q(theta)
    if not 0<=effort<=1 or not 0<=theta<=1:raise ValueError('rates')
    P=[];S=[]
    for n in range(7):
        a,b=rates(n)
        if clock:
            p,g=row(n,effort*a,effort*b)
            p=list(theta*x for x in p);p[n]+=1-theta
            g*=theta
        else:p,g=row(n,theta*effort*a,theta*effort*b)
        assert sum(p)==1 and g==theta*effort*(n*a+(6-n)*b)
        P.append(tuple(p));S.append(g)
    return tuple(P),tuple(S)


def total(n0,H=40,clock=False,effort=Q(1),fee=Q(0)):
    cost(n0)
    if not isinstance(H,int) or H<1 or fee<0:raise ValueError('H/fee')
    P,S=transition(clock,effort)
    dist=[Q(0)]*7;dist[n0]=Q(1)
    congestion=Q(0);revisions=Q(0)
    for t in range(H):
        congestion+=sum((dist[n]*cost(n) for n in range(7)),Q(0))
        if t==H-1:break
        revisions+=sum((dist[n]*S[n] for n in range(7)),Q(0))
        dist=[sum((dist[n]*P[n][m] for n in range(7)),Q(0)) for m in range(7)]
        assert sum(dist)==1
    return congestion,revisions,congestion+Q(fee)*revisions


def local_effect(n,effort=Q(1),theta=Q(1,2)):
    a,b=rates(n)
    return 3*theta*(1-theta)*effort**2*((((6-n)*b-n*a)**2)-(n*a*a+(6-n)*b*b))


def demo():
    n=4
    one=total(n,2,True)[0]-total(n,2,False)[0]
    forty=total(n,40,True)[0]-total(n,40,False)[0]
    assert one==local_effect(n)==-Q(3,5000)
    assert 24<forty<26
    return {'local_gap':float(one),'H40_gap':float(forty)}


if __name__=='__main__':print(demo())
