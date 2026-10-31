"""Tests against independently enumerated draw sequences and boundary cases."""
import itertools,numpy as np
from engine import exact_probabilities
A=[1.,2.];B=[0.,3.]
p=exact_probabilities(A,B,4)
for q in range(1,5):
    aa=[sum(x) for x in itertools.product(A,repeat=q)]
    bb=[sum(x) for x in itertools.product(B,repeat=q)]
    total=sum((x>y)+.5*(x==y) for x in aa for y in bb)/(len(aa)*len(bb))
    assert abs(total-p[q-1])<1e-10
assert np.allclose(exact_probabilities([1],[2]),0)
assert np.allclose(exact_probabilities([2],[1]),1)
assert np.allclose(exact_probabilities([2],[2]),.5)
assert np.allclose(exact_probabilities([],[]),.5)
print("all exact-engine tests pass")
