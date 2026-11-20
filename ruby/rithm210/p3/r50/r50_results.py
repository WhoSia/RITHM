"""Print exact lag curves and horizon summaries."""

import argparse
import json

from r50.r50_delay import results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all-lags", action="store_true")
    cases, sensitivity = results()
    if not parser.parse_args().all_lags:
        for case in cases.values():
            case["later_nonzero_count"] = sum(r["minus4_minus_plus4"] != 0 for r in case["lag"][6:])
            case["lag"] = case["lag"][:6]
    print(json.dumps({"cases": cases, "reward_retention_sensitivity": sensitivity}, indent=2, default=str))
