"""RITHM R66-T6 minimal source-free exact higher-order welfare witness.

Original congestion costs: C(n_A)=24+3(n_A-4)^2.
Two initial joint action laws agree on EVERY first/second moment but not
third-order co-switching. Same deterministic one-B-to-A recovery afterwards.
This is a synthetic counterexample, not an identified human mechanism.
"""
from fractions import Fraction as F
from itertools import product


def joint(parity):
    if parity not in (0, 1):
        raise ValueError("parity must be 0/1")
    return {x: F(1,4) for x in product((0,1), repeat=3)
            if sum(x)%2 == parity}


def triple(law):
    return sum((p*x[0]*x[1]*x[2] for x,p in law.items()), F(0))


def marginal(law, i):
    return sum((p*x[i] for x,p in law.items()), F(0))


def pair(law, i, j):
    return sum((p*x[i]*x[j] for x,p in law.items()), F(0))


def integrated_excess_given_initial_k(k):
    """3 Σ_{j=1}^k j² = (2 k³+3 k²+k)/2."""
    if type(k) is not int or not 0<=k<=3:
        raise ValueError("exactly three candidate agents")
    return k*(k+1)*(2*k+1)//2


def one_step_excess(law):
    return sum((p*3*sum(x)**2 for x,p in law.items()), F(0))


def horizon_40_excess(law):
    return sum((p*integrated_excess_given_initial_k(sum(x))
                for x,p in law.items()), F(0))


def gross_switches(law):
    # first initial flips K, plus precisely K deterministic later recovery flips
    return sum((p*2*sum(x) for x,p in law.items()), F(0))


def check():
    a,b=joint(0),joint(1)
    assert sum(a.values()) == sum(b.values()) == 1
    assert all(marginal(a,i)==marginal(b,i)==F(1,2) for i in range(3))
    assert all(pair(a,i,j)==pair(b,i,j)==F(1,4)
               for i in range(3) for j in range(i+1,3))
    assert (triple(a),triple(b))==(F(0),F(1,4))
    assert one_step_excess(a)==one_step_excess(b)==9
    assert horizon_40_excess(a)==F(45,4)  # 11.25
    assert horizon_40_excess(b)==F(51,4)  # 12.75
    assert gross_switches(a)==gross_switches(b)==3
    assert horizon_40_excess(b)-horizon_40_excess(a)==6*(triple(b)-triple(a))==F(3,2)
    return {"one_step_excess_each":str(one_step_excess(a)),
        "late_total_even":str(horizon_40_excess(a)),
        "late_total_odd":str(horizon_40_excess(b)),
        "long_horizon_odd_minus_even":"3/2",
        "expected_lifetime_gross_switches_each":"3",
        "physical_switch_fee_effect":"cancels for any fixed f"}


if __name__ == "__main__":
    import json
    print(json.dumps(check(),indent=2))
