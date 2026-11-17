"""Exact primal and dual certificates for the two frozen R43 cases."""
from fractions import Fraction as F

CEILINGS = {3: F(1862, 1249), 5: F(97, 103)}
EXPECTED = {
    3: (F(268, 321),)*3 + (F(613, 1284),)*3,
    5: (F(549, 755),)*5 + (F(53, 151),),
}


def dot(left, right):
    return sum(a*b for a, b in zip(left, right, strict=True))


def exact_cost(start, s):
    if s < 0:
        raise ValueError("expected nonnegative burden")
    if s > CEILINGS[start]:
        return None
    if start == 5:
        return F(6, 151)
    return F(81, 428)+F(106, 107)*max(s-1, 0)


def witness(start, s):
    if exact_cost(start, s) is None:
        raise ValueError("outside feasible range")
    if start == 5:
        return {(3, 0): F(2, 151), (3, 1): F(53, 151), (4, 0): F(96, 151)}
    t = F(53, 321)*max(s-1, 0)
    return {(2, 2): F(212, 428)-t, (2, 3): t,
            (3, 0): F(27, 428)+t, (3, 1): F(189, 428)-t}


def verify(data, start, marginals):
    """Check the whole interval by verifying affine certificates at segment endpoints."""
    if tuple(map(F, marginals)) != EXPECTED[start]:
        raise ValueError("certificate is scoped to the frozen R43 marginals")
    counts, eq, moments, gross, slopes, cost = data
    cap = CEILINGS[start]
    if start == 3:
        majorant, weights = (9, -3, 2), (0, 3, 1, 0)
    else:
        majorant, weights = (-19, 5, 6), (0, 1, 0, 0)
    ceiling_gap = [dot(majorant, a)-dot(weights, g)
                   for a, g in zip(zip(*eq), zip(*gross), strict=True)]
    if min(ceiling_gap) < 0 or dot(weights, slopes) <= 0:
        raise ArithmeticError("invalid ceiling dominance")
    if dot(majorant, moments)/dot(weights, slopes) != cap:
        raise ArithmeticError("invalid bound")
    segments = [(F(0), min(F(1), cap), (12, -3, -3), (0, 0, 0, 0))]
    if start == 3:
        segments.append((F(1), cap, (6, -1, -3), (0, 2, 0, 0)))
    for lo, hi, coeff, multipliers in segments:
        if min(multipliers) < 0 or any(
            dot(coeff, a)+dot(multipliers, g) > c
            for a, g, c in zip(zip(*eq), zip(*gross), cost, strict=True)
        ):
            raise ArithmeticError("invalid dual lower bound")
        for s in (lo, hi):
            law = witness(start, s)
            q = [law.get(k, F(0)) for k in counts]
            if min(q) < 0 or tuple(dot(a, q) for a in eq) != moments:
                raise ArithmeticError("invalid primal moments")
            if any(dot(g, q) < s*v for g, v in zip(gross, slopes, strict=True)):
                raise ArithmeticError("invalid obedience witness")
            lower = dot(coeff, moments)+s*dot(multipliers, slopes)
            if dot(cost, q) != lower or lower != exact_cost(start, s):
                raise ArithmeticError("primal and dual costs disagree")
    return True


def restore_four_at_five(s):
    """Smallest total change of individual marginals for certain 4:2, if feasible."""
    if not 0 <= s <= 1:
        raise ValueError("certain 4:2 is incompatible with obedience at this burden")
    # The initial B's marginal stays fixed. Initial A actors are exchangeable.
    law = {(3, 1): F(53, 151), (4, 0): F(98, 151)}
    initial_a_p = dot([x for x, _ in law], law.values())/5
    return {"initial_A_probability": str(initial_a_p), "initial_B_probability": "53/151",
            "minimum_total_absolute_marginal_change": str(F(4)-sum(EXPECTED[5])),
            "law": {f"{x},{y}": str(w) for (x, y), w in law.items()}}
