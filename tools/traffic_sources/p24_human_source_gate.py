"""P24 source-derived audit: virtual upstream count, not a physical sensor."""
import csv
import json
from pathlib import Path
from collections import defaultdict

def audit(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==24
    observed=[]
    for r in rows:
        a=int(r["choices_base3_hex"],16)
        seq=[]
        for _ in range(240):
            a,d=divmod(a,3)
            seq.append(d+1)
        assert a==0
        seq.reverse()
        bits=int(r["incident_20_bits_hex"],16)
        assert bits.bit_count()==4
        for t in range(20):
            s=seq[12*t:12*(t+1)]
            n1,n2,n3=(s.count(i) for i in (1,2,3))
            z=(bits>>(19-t))&1
            C=264-24*n1-9*n2+2*n1*n1+2*n1*n2+n2*n2+19*z*n2
            observed.append((r["session"],int(r["group"]),int(r["stage"]),n2+n3,z,C))
    assert len(observed)==480
    a=[v[5] for v in observed if v[3]==8 and v[4]==0]
    by=defaultdict(list)
    for s,g,t,q,z,c in observed:
        by[s,g,t,q,z].append(c)
    return {"sessions":len({v[0] for v in observed}),
            "panels":len(rows),"group_rounds":len(observed),
            "q8_z0_n":len(a),"q8_z0_cost_range":[min(a),max(a)],
            "within_panel_ambiguous_strata":sum(len(v)>1 and min(v)<max(v) for v in by.values()),
            "limitation":"route-choice-derived virtual detector; no receipts; no causal effect"}

if __name__=="__main__":
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2))
