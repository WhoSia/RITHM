#!/usr/bin/env python3
"""P22: source measurement, provider publication, client receipt; no live source clock."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
import json
from pathlib import Path

def check_time(t):
    if not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("Timezone-aware datetime required")
    return t.astimezone(timezone.utc)

@dataclass(frozen=True)
class Evidence:
    observation_end: datetime
    first_positive_receipt: Optional[datetime]=None
    last_negative_poll: Optional[datetime]=None
    negative_poll_is_authoritative: bool=False
    trusted_client_receipt: bool=False
    def __post_init__(self):
        e=check_time(self.observation_end)
        p=check_time(self.first_positive_receipt) if self.first_positive_receipt is not None else None
        n=check_time(self.last_negative_poll) if self.last_negative_poll is not None else None
        if p is not None and p<e:raise ValueError("Receipt before observation ended")
        if n is not None and n<e:raise ValueError("Negative poll before interval end")
        if self.negative_poll_is_authoritative and n is None:
            raise ValueError("Authoritative absence claim without poll")
        if self.trusted_client_receipt and p is None:
            raise ValueError("Trusted receipt missing timestamp")
        if self.negative_poll_is_authoritative and n is not None and p is not None and n>=p:
            raise ValueError("Negative poll must precede first positive")

    def provider_window(self):
        lower=self.last_negative_poll if self.negative_poll_is_authoritative else self.observation_end
        # Only TRUSTED positive receipt provides a provider publication upper bound.
        upper=self.first_positive_receipt if self.trusted_client_receipt else None
        return check_time(lower),(check_time(upper) if upper is not None else None)

    def provider_status(self,decision_time):
        when=check_time(decision_time)
        lower,upper=self.provider_window()
        if when<check_time(self.observation_end):return "impossible"
        if upper is not None and upper<=when:return "certain"
        if self.negative_poll_is_authoritative and lower>=when:return "impossible"
        return "ambiguous"

    def operationally_receipted(self,decision_time):
        when=check_time(decision_time)
        p=self.first_positive_receipt
        return bool(self.trusted_client_receipt and p is not None and
                    check_time(p)<=when and check_time(self.observation_end)<=when)

def source_pair_legal(a:Evidence,b:Evidence,decision_time):
    if check_time(b.observation_end)-check_time(a.observation_end)!=timedelta(minutes=5):
        raise ValueError("Nonconsecutive five-minute source halves")
    return a.operationally_receipted(decision_time) and b.operationally_receipted(decision_time)

def allowed_latest_pair(pairs,decision_time):
    valid=[(check_time(b.observation_end),(a,b)) for a,b in pairs
           if source_pair_legal(a,b,decision_time)]
    return max(valid,key=lambda x:x[0])[1] if valid else None

# Rounded P21 2025 source scores from authenticated GitHub P21 table;
# not a NEW raw 38-shard replay; not measured actual publication timestamps.
P21_N=2121699
P21_LAGS={
 1:{"calendar":66.649,"fixed":34.249,"link_switch":34.249},
 2:{"calendar":66.649,"fixed":44.955,"link_switch":45.957},
 3:{"calendar":66.649,"fixed":53.927,"link_switch":52.653},
 4:{"calendar":66.649,"fixed":61.715,"link_switch":55.887},
 5:{"calendar":66.649,"fixed":68.998,"link_switch":58.128},
 6:{"calendar":66.649,"fixed":75.721,"link_switch":60.165},
 7:{"calendar":66.649,"fixed":82.417,"link_switch":61.849}
}

def lag_from_bound(delay_minutes):
    if isinstance(delay_minutes,bool) or not isinstance(delay_minutes,int) or delay_minutes<0:
        raise ValueError("Nonnegative integer minute bound needed")
    return 1+(delay_minutes+9)//10

def scenario_court():
    rows=[]
    for lag,score in P21_LAGS.items():
        oracle=min(score.values())
        rows.append({"lag":lag,"calendar":score["calendar"],"fixed":score["fixed"],
            "link_switch":score["link_switch"],
            "expost_best_of_three_ILLEGAL_SELECTOR":oracle,
            "calendar_regret":round(score["calendar"]-oracle,3),
            "frozen_lag7_gate_regret":round(P21_LAGS[7]["link_switch"]-oracle,3)})
    return {"status":"NO_MEASURED_PROVIDER_OR_CLIENT_RELEASE_CLOCK",
            "source_P21_matched_mask_N":P21_N,
            "2025_scores_are_P21_rounded_reproductions_NOT_new_replay":True,
            "client_max_delay_60min_CERTIFIED":False,
            "if_client_bound_D60_certified_then_frozen_lag7_gate":P21_LAGS[7]["link_switch"],
            "calendar_retrospective_MAE":66.649,
            "conditional_D60_gate_gain_vs_calendar":4.800,
            "max_scenario_aggregate_regret_across_these_replayed_options":{
               "frozen_lag7_gate":27.600,"calendar":32.400},
            "not_minimax_optimality_or_operational_claim":True,
            "not_causal_guidance_or_human_welfare":True,
            "scenarios":rows}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(scenario_court(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CONDITIONAL COURT PASS; REAL PROVIDER CLOCK ABSENT")
