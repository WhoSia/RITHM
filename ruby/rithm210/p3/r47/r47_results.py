"""Print the pinned R47 horizon table and sensitivity sweep."""

import json
from fractions import Fraction as Q

from r47_withdrawal import benchmarks, checkpoint_selection


def main():
    cases = benchmarks()
    output = {
        "retention": "3/4",
        "checkpoints": (1, 2, 3, 5, 10, 20, 40),
        "cases": {name: [rows[t-1] for t in (1, 2, 3, 5, 10, 20, 40)]
                  for name, rows in cases.items()},
        "checkpoint_selection": checkpoint_selection(),
        "correction_congestion_sensitivity": {
            str(p): benchmarks(retention=p)["correction_memory"][-1]["congestion"]
                    - cases["correction_no_memory"][-1]["congestion"]
            for p in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(9, 10), Q(1))
        },
    }
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
