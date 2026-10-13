"""RITHM-2.7 P25: finite stage-C route-welfare bounds around ACTUAL 2017 human routes.

Extra hypothetical advice is offered AFTER upstream A-C entry; keep initial
route occupancy and incident fixed, allow at most k C-B/C-D switches.
Not observed policy uptake, not a causal comparison of information arms.
"""
import csv
import json
import sys
from pathlib import Path


def network_cost(n1, n2, z):
    return 264 - 24*n1 - 9*n2 + 2*n1*n1 + 2*n1*n2 + n2*n2 + 19*z*n2


def source_states(filename):
    with open(filename, encoding="utf8", newline="") as f:
        panels = list(csv.DictReader(f))
    assert len(panels) == 24
    states = []
    for p in panels:
        code = int(p["choices_base3_hex"], 16)
        routes = []
        for _ in range(240):
            code, digit = divmod(code, 3)
            routes.append(digit + 1)
        assert code == 0
        routes.reverse()
        incidents = int(p["incident_20_bits_hex"], 16)
        assert incidents.bit_count() == 4
        for t in range(20):
            block = routes[12*t:12*(t+1)]
            n1, n2, n3 = [block.count(k) for k in (1, 2, 3)]
            z = (incidents >> (19-t)) & 1
            states.append({"session":p["session"], "group":int(p["group"]),
                           "stage":int(p["stage"]), "t":t+1, "info":int(p["info"]),
                           "n1":n1, "n2":n2, "n3":n3, "z":z,
                           "C":network_cost(n1,n2,z)})
    assert len(states) == 480
    return states


def local_gain_bounds(x, max_switch):
    q = x["n2"] + x["n3"]
    low = max(0, x["n2"] - max_switch)
    high = min(q, x["n2"] + max_switch)
    gains = [x["C"]-network_cost(x["n1"], n2, x["z"])
             for n2 in range(low, high+1)]
    return min(gains), max(gains)


def summary(states, budgets=(1,2,12)):
    output = {}
    for k in budgets:
        bb = [local_gain_bounds(x,k) for x in states]
        output[str(k)] = {
            "N":len(bb),
            "both_signs_feasible":sum(lo < 0 < hi for lo,hi in bb),
            "harm_feasible":sum(lo < 0 for lo,hi in bb),
            "benefit_feasible":sum(hi > 0 for lo,hi in bb),
            "mean_lower":sum(lo for lo,hi in bb)/len(bb),
            "mean_upper":sum(hi for lo,hi in bb)/len(bb)
        }
    return {"source":"2017 verified compact human routes; 480 group rounds",
            "restriction":"same upstream A-C entry and incident; at most k new hypothetical eligible C switches",
            "warning":"No observed policy response; separately attained per-round extrema are not one dynamic policy",
            "bounds":output}


if __name__=="__main__":
    root = Path(__file__).resolve().parents[2]
    source = Path(sys.argv[1]) if len(sys.argv)>1 else root/"data"/"rithm23_wijayaratna2017_routes.csv"
    result=summary(source_states(source))
    assert result["bounds"]["1"]["both_signs_feasible"] == 369
    print(json.dumps(result,indent=2))
