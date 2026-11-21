"""Non-strict discrete Lyapunov decrease does not alone imply attraction.

Audits a GENERIC implication as printed in Yang et al. 2026 Proposition 3,
not the paper's concrete full-information dynamics.
"""
from fractions import Fraction as F

def identity_map(x):return F(x)
def sign_flip_map(x):return -F(x)
def lyapunov(x):return F(x)**2
def nonincrease_holds(points,dynamics):
    return all(lyapunov(dynamics(x))<=lyapunov(x) for x in points)
def is_attracted_within(dynamics,x,horizon,tolerance=F(1,1000)):
    if not isinstance(horizon,int) or horizon<1:raise ValueError('horizon')
    y=F(x)
    for _ in range(horizon):y=dynamics(y)
    return abs(y)<=F(tolerance)
