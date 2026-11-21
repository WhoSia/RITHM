"""R59 exact transport obstruction: same history-wise likelihood, different rollout.

Two six-seat labelled states have A occupancy 4 (m0) and 5 (m1). The
observed source-free history stays at m0. Transition kernels agree exactly
on every *observed* conditional decision, but disagree off that path.
"""
from fractions import Fraction
from math import log

M0=0b001111  # 4 A
M1=0b011111  # 5 A


def transition(state, *, mechanism):
    if mechanism not in ('reset','trap') or state not in (M0,M1):
        raise ValueError('unknown state or kernel')
    if state==M0:
        return {M0:Fraction(9,10), M1:Fraction(1,10)}
    if mechanism=='reset':return {M0:Fraction(1),M1:Fraction(0)}
    return {M0:Fraction(0),M1:Fraction(1)}


def exact_rollout(*,periods=40,mechanism):
    if type(periods) is not int or periods<1:raise ValueError('positive horizon')
    masses={M0:Fraction(1),M1:Fraction(0)}
    per_period=[]
    total_excess=Fraction(0)
    total_gross=Fraction(0)
    for t in range(1,periods+1):
        nxt={M0:Fraction(0),M1:Fraction(0)}
        switches=Fraction(0)
        for old,pold in masses.items():
            for new,p in transition(old,mechanism=mechanism).items():
                nxt[new]+=pold*p
                switches+=pold*p*(old^new).bit_count()
        if sum(nxt.values())!=1:raise AssertionError('normalization')
        masses=nxt
        stage_excess=3*nxt[M1]
        total_excess+=stage_excess
        total_gross+=switches
        per_period.append({'t':t,'prob_5A':nxt[M1],
                           'mean_excess':stage_excess,'gross_changes':switches})
    return {'periods':per_period,'expected_total_excess':total_excess,
            'expected_total_gross':total_gross,'final_5A_probability':masses[M1]}


def observed_one_step_loss(mechanism,*,horizon=40):
    """Same all-M0 observed path and identical per-step score in both worlds."""
    if horizon<1:raise ValueError('positive history')
    law=transition(M0,mechanism=mechanism)
    return -horizon*log(float(law[M0]))


if __name__=='__main__':
    for name in ('reset','trap'):
        z=exact_rollout(mechanism=name)
        print(name, 'heldout loss', observed_one_step_loss(name),
              '40-step expected excess',float(z['expected_total_excess']),
              'gross',float(z['expected_total_gross']))
