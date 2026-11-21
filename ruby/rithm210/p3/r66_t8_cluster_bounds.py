"""Conservative simultaneous session-level ratio moment confidence region.

Assumes 24 independent and identically distributed whole sessions and
A_{d,s} in [0,B_s], B_s in [0,BMAX]. Never resample individual decisions.
"""
from decimal import Decimal,localcontext,ROUND_CEILING
from fractions import Fraction as F

def union_hoeffding_radius(num_sessions,bmax,num_moments,alpha=F(1,20),digits=9):
    if not isinstance(num_sessions,int) or num_sessions<1 or not isinstance(bmax,int) or bmax<1 or not isinstance(num_moments,int) or num_moments<1:
        raise ValueError('invalid study support')
    if not 0<F(alpha)<1:raise ValueError('alpha between zero and one')
    if not 1<=digits<=16:raise ValueError('precision digits')
    with localcontext() as ctx:
        ctx.prec=75
        x=Decimal(2*(num_moments+1))*Decimal(F(alpha).denominator)/Decimal(F(alpha).numerator)
        e=Decimal(bmax)*(x.ln()/(Decimal(2)*Decimal(num_sessions))).sqrt()
        return F(e.quantize(Decimal(1).scaleb(-digits),rounding=ROUND_CEILING))

def ratio_interval(numerators,denominators,*,bmax,num_moments=1,alpha=F(1,20)):
    if len(numerators)!=len(denominators) or not numerators:
        raise ValueError('one matched independent cluster per row')
    if any(not 0<=F(a)<=F(b)<=bmax for a,b in zip(numerators,denominators)):
        raise ValueError('numerator must lie inside denominator per session')
    n=len(numerators)
    e=union_hoeffding_radius(n,bmax,num_moments,alpha)
    ah=sum(map(F,numerators),F(0))/n
    bh=sum(map(F,denominators),F(0))/n
    blo=max(F(0),bh-e)
    bhi=min(F(bmax),bh+e)
    alo=max(F(0),ah-e)
    ahi=min(F(bmax),ah+e)
    if blo==0:return F(0),F(1),e
    return max(F(0),alo/bhi),min(F(1),ahi/blo),e
