"""R25: source-free exact counterfactual group residual controls.

Individual probability calibration must precede residual-pair claims. Even
correct marginal calibration is insufficient to eliminate a shared latent
shock: two observably distinct data-generating laws may share actor marginals.
"""
from itertools import product
from r24_welfare_attribution import decompose


def independent_exact(true_p,forecast_p):
    """Expected six-person pair error for independent true Bernoulli actors."""
    if len(true_p)!=6 or len(forecast_p)!=6:
        raise ValueError('six people')
    accum=0.
    for choices in product((0,1),repeat=6):
        mass=1.
        for y,p in zip(choices,true_p):mass*=p if y else 1-p
        r=decompose(list(choices),forecast_p,[1,1,1,0,0,0])
        accum+=mass*(r['same_pair']+r['opposite_pair'])
    return accum


def common_shock_exact(forecast_p=(.5,)*6):
    """All actors copy a fair shared latent bit; marginal P(A) remains .5."""
    return sum(.5*sum(decompose([bit]*6,list(forecast_p),[1,1,1,0,0,0])[k]
                    for k in ('same_pair','opposite_pair')) for bit in (0,1))


def demo():
    return {'independent_miscalibrated':independent_exact([.7]*6,[.5]*6),
            'independent_calibrated':independent_exact([.7]*6,[.7]*6),
            'shared_latent_shock_with_correct_marginals':common_shock_exact()}

if __name__=='__main__':
    import json
    print(json.dumps(demo(),indent=2))
