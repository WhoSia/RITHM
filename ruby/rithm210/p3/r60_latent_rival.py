"""R60 exact nonidentification witness over TWO observed section summaries.

Warning: equality for two binary segment summaries does NOT imply equality of
all within-segment trajectories or a third segment. Both histories admit more
specific tests given additional observations.
"""
from fractions import Fraction as F
from itertools import product


def fixed_type_law():
    types=(F(1,5),F(4,5))
    return {(a,b):sum(F(1,2)*(p if a else 1-p)*(p if b else 1-p)
                      for p in types) for a,b in product((0,1), repeat=2)}


def history_learning_law():
    # Draw first section's binary summary fairly. After it, change conditional
    # second-section propensity as if the first observation was learned.
    return {(a,b):F(1,2)*(F(17,25) if a==b else F(8,25))
            for a,b in product((0,1), repeat=2)}


def exact_nonidentification():
    fixed=fixed_type_law();learn=history_learning_law()
    if fixed!=learn:raise AssertionError('two mechanisms differ on observable law')
    if sum(fixed.values())!=1:raise AssertionError('invalid law')
    return {'pairs':{str(key):str(value) for key,value in sorted(fixed.items())},
            'match_probability':str(fixed[0,0]+fixed[1,1]),
            'identified':'only the two-section joint binary summary distribution',
            'unidentified':'persistent actor type versus history-response mechanism',
            'not_equivalent':'complete 40-period within-section histories or all three segments'}


if __name__=='__main__':
    import json
    print(json.dumps(exact_nonidentification(),indent=2,sort_keys=True))
