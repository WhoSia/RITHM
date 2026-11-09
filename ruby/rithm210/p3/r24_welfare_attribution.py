"""RITHM R24: exact six-actor independent-forecast quadratic-cost error ledger.

Route-choice forecasts (not A->B switching probabilities). Pair products are
descriptive residual terms; nonzero terms never prove peer effects or causality.
"""
import itertools
import math

def cost(n):
    if type(n) is not int or not 0 <= n <= 6:
        raise ValueError("integer occupancy 0..6 needed")
    return 24 + 3 * (n - 4) ** 2

def distribution(probabilities):
    if len(probabilities) != 6 or any(
            not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1
            for p in probabilities):
        raise ValueError("six valid independent actor probabilities required")
    state = [1.]
    for p in probabilities:
        nxt = [0.] * (len(state) + 1)
        for i, mass in enumerate(state):
            nxt[i] += mass * (1-p)
            nxt[i+1] += mass * p
        state = nxt
    if not math.isclose(sum(state), 1., abs_tol=1e-10):
        raise ArithmeticError("group forecast probability mass")
    return state

def decompose(actual_routes, probabilities, previous_routes=None):
    if len(actual_routes) != 6 or any(type(y) is not int or y not in (0,1)
                                       for y in actual_routes):
        raise ValueError("six binary actual routes required")
    if previous_routes is not None and (
            len(previous_routes) != 6 or
            any(type(y) is not int or y not in (0,1) for y in previous_routes)):
        raise ValueError("previous route cohort must contain six binary routes")
    dist = distribution(probabilities)
    n = sum(actual_routes)
    mu = sum(probabilities)
    e = [y-p for y,p in zip(actual_routes, probabilities)]
    var = sum(p*(1-p) for p in probabilities)
    linear = 6*(mu-4)*sum(e)
    diagonal = 3*sum(v*v-p*(1-p) for v,p in zip(e,probabilities))
    same = opposite = unclassified = 0.
    for i,j in itertools.combinations(range(6),2):
        term=6*e[i]*e[j]
        if previous_routes is None:
            unclassified+=term
        elif previous_routes[i] == previous_routes[j]:
            same+=term
        else:
            opposite+=term
    predicted=24+3*((mu-4)**2+var)
    actual=cost(n)
    error=actual-predicted
    if not math.isclose(error,linear+diagonal+same+opposite+unclassified,
                        abs_tol=1e-9,rel_tol=1e-11):
        raise ArithmeticError("exact welfare identity mismatch")
    return dict(observed_cost=actual,predicted_cost=predicted,
                welfare_error=error,linear=linear,diagonal=diagonal,
                same_pair=same,opposite_pair=opposite,
                unknown_pair=unclassified,
                logloss=-math.log(max(dist[n],1e-300)),
                abs_cost_error=abs(error),
                actor_brier=sum(v*v for v in e)/6.,
                mean_actor_error=sum(e)/6.)
