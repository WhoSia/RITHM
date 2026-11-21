"""Seven occupancy states, six players, exact congestion and simple recovery policy."""
from fractions import Fraction as F
from r66_t7_transfer import J


def total_congestion(n):
    if not isinstance(n,int) or not 0<=n<=6:
        raise ValueError("nA must be between 0 and 6")
    return n*n+2*(6-n)*(6-n)


def extra_congestion(n):
    return total_congestion(n)-24


def deterministic_single_step_recovery():
    """Takes exactly one flow unit toward system optimum nA=4 per step."""
    P=[[F(0) for _ in range(7)] for _ in range(7)]
    for n in range(7):
        nxt=n+1 if n<4 else (n-1 if n>4 else n)
        P[n][nxt]=F(1)
    return tuple(tuple(row) for row in P)


def welfare_from_initial(initial,horizon):
    if not 0<=initial<=6:
        raise ValueError("bad occupancy")
    mu=tuple(F(int(n==initial)) for n in range(7))
    return J(mu,deterministic_single_step_recovery(),tuple(F(extra_congestion(i)) for i in range(7)),horizon)
