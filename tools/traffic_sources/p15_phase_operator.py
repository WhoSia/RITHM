#!/usr/bin/env python3
"""P15 exact two-bin 5min source aggregation kernel.
A constructive identification witness; NEVER proof of traffic detector malfunction.
"""
from math import isfinite

def aggregate_ten_min(five_min_counts):
    if len(five_min_counts) % 2:
        raise ValueError("Need complete pairs of two consecutive 5min bins")
    if not all(isfinite(v) and v >= 0 for v in five_min_counts):
        raise ValueError("Counts must be finite and nonnegative")
    return [five_min_counts[2*k] + five_min_counts[2*k+1]
            for k in range(len(five_min_counts)//2)]

def competing_worlds(y_even, y_odd):
    """Same two recorded counts, different feasible latent physical worlds.

    A: true physical count equals observed, zero measurement component.
    B: true physical counts equal within a ten-minute pair, measurement
       component sums to zero over the same pair.

    Existence of B does NOT imply the source has such an error.
    """
    if not all(isfinite(v) and v>=0 for v in (y_even,y_odd)):
        raise ValueError("Need finite nonnegative original source counts")
    avg=(y_even+y_odd)/2
    return {
      "observed": [y_even,y_odd],
      "physical_world": {"latent_true_counts":[y_even,y_odd],
                         "measurement_component":[0.,0.]},
      "redistribution_world": {"latent_true_counts":[avg,avg],
                               "measurement_component":[y_even-avg,y_odd-avg]},
      "identified_ten_min_total": y_even+y_odd,
      "unidentified_first_five_min_true_count_range": [0.,y_even+y_odd],
      "per_bin_reassignment_to_flatten_phase": abs(y_even-y_odd)/2
    }

def audit_worlds(w):
    y=w["observed"];t=sum(y)
    for name in ("physical_world","redistribution_world"):
        q=w[name]["latent_true_counts"]
        m=w[name]["measurement_component"]
        if any(z<0 for z in q) or abs(sum(q)-t)>1e-9:
            raise AssertionError("Nonnegative flow/pair conservation violated")
        if abs(sum(m))>1e-9 or any(abs(qi+mi-yi)>1e-9 for qi,mi,yi in zip(q,m,y)):
            raise AssertionError("Measurement decomposition mismatch")
    return True

if __name__=="__main__":
    import json
    r=competing_worlds(315.,557.)
    assert audit_worlds(r)
    print(json.dumps(r,ensure_ascii=False,indent=2))
