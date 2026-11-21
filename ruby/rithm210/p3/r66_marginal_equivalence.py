"""RITHM 2.10 R66-T1: exact finite-group micro->macro covariance bridge.

Pure mathematics, source-free. This is an analytical benchmark, NOT a novel
probability theorem and NOT an empirically identified cognitive mechanism.
The n=5 actors below are given a COMMON previous-occupancy snapshot: this
cannot be attributed to an uninformed experimental participant.
"""
from fractions import Fraction as F
from itertools import product


def social_excess(n, target=4, lam=3):
    if type(n) is not int or not 0 <= n <= 6:
        raise ValueError('six-person occupancy must be 0..6 integer')
    return F(lam) * (n-target)**2


def exact_joint_moments(n, directions, joint):
    """joint maps 0/1 six-agent flip patterns to mass; inactive actors allowed.

    directions[i] is +1 for a prior B actor, -1 for a prior A actor.
    An ineligible actor simply has zero switching probability.
    Prior routes must be consistent with the initial n occupancy.
    """
    if len(directions)!=6 or sum(d == -1 for d in directions)!=n:
        raise ValueError('the signed actor map must agree with n previous A users')
    if any(d not in (-1,1) for d in directions):
        raise ValueError('all actors must have a previous route (+1 B or -1 A)')
    if sum(joint.values(),F(0))!=F(1):raise ValueError('joint law not normalized')
    if any(len(b)!=6 or any(x not in (0,1) for x in b) or m<0 for b,m in joint.items()):
        raise ValueError('joint law invalid')
    p=[sum((m for b,m in joint.items() if b[i]),F(0)) for i in range(6)]
    e_excess=sum(m*social_excess(n+sum(d*x for d,x in zip(directions,b))) for b,m in joint.items())
    e_gross=sum(m*sum(b) for b,m in joint.items())
    signed_mean=sum(d*x for d,x in zip(directions,p))
    independent_variance=sum(x*(1-x) for x in p)
    covariance_welfare=F(0)
    for i in range(6):
        for j in range(i+1,6):
            both=sum((m for b,m in joint.items() if b[i] and b[j]),F(0))
            covariance_welfare+=2*directions[i]*directions[j]*(both-p[i]*p[j])
    reconstructed=3*((n-4+signed_mean)**2+independent_variance+covariance_welfare)
    if reconstructed!=e_excess:
        raise AssertionError('second-moment identity violated')
    return {'marginals':p,'expected_excess':e_excess,'expected_gross_switches':e_gross,
            'independent_variance':independent_variance,
            'signed_covariance_contribution':covariance_welfare,
            'reconstructed_excess':reconstructed}


def joint_independent(n, p):
    if len(p)!=6 or any(not 0<=x<=1 for x in p):raise ValueError('six legal probabilities')
    directions=tuple([-1]*n+[1]*(6-n))
    law={bits:F(1) for bits in product((0,1), repeat=6)}
    for bits in law:
        for x,prob in zip(bits,p):law[bits]*=prob if x else 1-prob
    return exact_joint_moments(n,directions,law)


def joint_common_update(n, eligible, mu):
    """One public clock controls all eligible route changes; others stay."""
    if len(eligible)!=6 or any(v not in (0,1) for v in eligible) or not 0<=mu<=1:
        raise ValueError('eligible and mean')
    stay=(0,)*6; move=tuple(eligible)
    joint={stay:1-mu,move:mu} if any(move) else {stay:F(1)}
    return exact_joint_moments(n,tuple([-1]*n+[1]*(6-n)),joint)


def mix_revision_clock(n, eligible, clock):
    """P(X_i=1|R)=R for eligible actors, independent conditional on R.
    clock: finite distribution over rational probabilities R.
    """
    if len(eligible)!=6 or any(v not in (0,1) for v in eligible):raise ValueError('eligible')
    if sum(clock.values(),F(0))!=1 or any(not 0<=r<=1 or w<0 for r,w in clock.items()):
        raise ValueError('clock must be a probability distribution')
    law={}
    for bits in product((0,1),repeat=6):
        value=F(0)
        for r,w in clock.items():
            mass=w
            for e,bit in zip(eligible,bits):
                mass*= (r if bit else 1-r) if e else (1 if not bit else 0)
            value+=mass
        law[bits]=value
    return exact_joint_moments(n,tuple([-1]*n+[1]*(6-n)),law)


def analytic_one_direction_delta(m, lam, clock):
    """Exact Jensen gap vs fixed-rate independent updating, same E[R]."""
    if not 0<=m<=6 or m!=int(m) or lam<0:raise ValueError('count/convexity')
    if sum(clock.values(),F(0))!=1:raise ValueError('clock normalization')
    mean=sum(r*w for r,w in clock.items())
    variance=sum((r-mean)**2*w for r,w in clock.items())
    return F(lam)*m*(m-1)*variance


def demo():
    mu=F(1,5)
    eligible=[1]*5+[0]
    indep=joint_independent(5,[mu]*5+[F(0)])
    shared=mix_revision_clock(5,eligible,{F(0):F(4,5),F(1):F(1,5)})
    assert indep['expected_excess']==F(12,5)
    assert shared['expected_excess']==F(12)
    assert shared['expected_excess']-indep['expected_excess']==analytic_one_direction_delta(5,3,{F(0):F(4,5),F(1):F(1,5)})
    return {'nA_before':5,'eligible_A_actors':5,'individual_switch_probability':'1/5',
            'independent_expected_excess':'12/5','all_or_none_common_clock_expected_excess':'12',
            'gap':'48/5','both_expected_gross_switches':'1',
            'interpretation':'identical individual means, macro welfare differs due to signed switch covariance; synthetic model'}


if __name__=='__main__':
    import json
    print(json.dumps(demo(),indent=2))
