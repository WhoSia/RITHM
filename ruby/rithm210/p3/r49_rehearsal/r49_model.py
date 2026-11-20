"""Pure phase and outcome helpers for the R49 six-seat rehearsal."""

SEATS = 6
PAYOUT_ROUND = 2
TARGET_A = 4
HORIZONS = (5, 10, 40)
FRAMES = ("route", "wallet")
AMOUNTS = (-4, 4)
PROTOCOL = "rithm-r49-rehearsal-v1"


def from_events(events):
    setup, *tail = events
    routes = setup["routes"].copy()
    for event in tail:
        if event["type"] == "choice_committed":
            routes[event["seat"]] = event["route"]
    return setup, routes


def next_state(events):
    setup, routes = from_events(events)
    last = events[-1]
    step = last["round"]
    kind = last["type"]
    if step == PAYOUT_ROUND and kind in ("settlement_assigned", "settlement_issued"):
        return {"phase": "settlement", "round": step, "seat": setup["focal"]}
    if step == setup["rounds"] and kind == "choice_committed":
        return {"phase": "complete"}
    if kind == "opportunity_opened":
        return {"phase": "choice", "round": step, "seat": last["seat"],
                "previous": last["previous"], "a": last["a"],
                "cost_A": last["cost_A"], "cost_B": last["cost_B"]}
    following = step + 1
    seat = setup["clock"][following - 1]
    return {"phase": "handoff", "round": following, "seat": seat}


def outcome(events):
    """Use logged decisions to measure correction, relapse and exposure order."""
    setup, _ = from_events(events)
    choices = [e for e in events if e["type"] == "choice_committed"]
    focal = setup["focal"]
    ack = next(e for e in events if e["type"] == "settlement_acknowledged")
    first_focal = next((e for e in choices if e["seq"] > ack["seq"] and e["seat"] == focal), None)
    before_focal = [e for e in choices if e["seq"] > ack["seq"] and e["seat"] != focal
                    and (first_focal is None or e["seq"] < first_focal["seq"])]
    first_hit = 0 if setup["start"] == TARGET_A else next(
        (e["round"] for e in choices if e["after_A"] == TARGET_A), None)
    first_exit = next((e["round"] for e in choices if first_hit is not None
                       and e["round"] > first_hit and e["after_A"] != TARGET_A), None)
    focal_moves = sum(e["seat"] == focal and e["previous"] != e["route"] for e in choices)
    congestion = sum(3 * (e["after_A"] - TARGET_A)**2 for e in choices)
    return {
        "first_hit_round": first_hit,
        "first_exit_round": first_exit,
        "pre_settlement_A": choices[PAYOUT_ROUND - 1]["after_A"],
        "first_focal_after_settlement": None if first_focal is None else {
            "round": first_focal["round"], "switched": first_focal["previous"] != first_focal["route"],
            "choice_seq": first_focal["seq"],
        },
        "other_choices_before_focal": [e["seq"] for e in before_focal],
        "other_switches_before_focal": sum(e["previous"] != e["route"] for e in before_focal),
        "congestion_cost": congestion,
        "focal_switches": focal_moves,
        "modeled_total_cost_half_points": 2 * congestion + focal_moves,
    }
