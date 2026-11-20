"""SQLite state machine for a single-device, six-seat rehearsal."""

import json
import re
import secrets
import sqlite3
import time
from contextlib import closing, contextmanager

from r49_model import (
    AMOUNTS, FRAMES, HORIZONS, PAYOUT_ROUND, PROTOCOL, SEATS, from_events, next_state, outcome,
)


class Conflict(ValueError):
    pass


class Ledger:
    def __init__(self, path, rng=None):
        self.path = path
        self.rng = rng if rng is not None else secrets.SystemRandom()
        with self.connect(write=True) as db:
            db.execute("CREATE TABLE IF NOT EXISTS r49_events "
                       "(study TEXT, seq INTEGER, payload TEXT NOT NULL, PRIMARY KEY(study, seq))")

    @contextmanager
    def connect(self, write=False):
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield db

    @staticmethod
    def load(db, study):
        return [json.loads(row[0]) for row in db.execute(
            "SELECT payload FROM r49_events WHERE study=? ORDER BY seq", (study,))]

    @staticmethod
    def record(db, study, events, kind, round_, **payload):
        seq = len(events) + 1
        event = dict(type=kind, round=round_, seq=seq, server_unix_ns=time.time_ns(), **payload)
        db.execute("INSERT INTO r49_events VALUES (?, ?, ?)", (study, seq, json.dumps(event)))
        events.append(event)
        return event

    def allocate(self, study, start, rounds):
        if not isinstance(study, str) or not re.fullmatch(r"[a-f0-9]{32}", study):
            raise ValueError("invalid rehearsal key")
        if type(start) is not int or start not in (4, 5) or type(rounds) is not int or rounds not in HORIZONS:
            raise ValueError("invalid initial position or horizon")
        with self.connect(write=True) as db:
            events = self.load(db, study)
            if events:
                params = events[0]
                if (params["start"], params["rounds"]) != (start, rounds):
                    raise Conflict("allocation key already used")
                return
            routes = ["A"] * start + ["B"] * (SEATS - start)
            self.rng.shuffle(routes)
            eligible = [i for i, route in enumerate(routes) if route == ("A" if start == 5 else "B")]
            focal = self.rng.choice(eligible)
            clock = [self.rng.randrange(SEATS) for _ in range(rounds)]
            self.record(db, study, events, "allocated", 0, start=start, rounds=rounds,
                        routes=routes, focal=focal, clock=clock)

    def view(self, study):
        with self.connect() as db:
            events = self.load(db, study)
        if not events:
            raise KeyError("unknown rehearsal")
        return next_state(events)

    def action(self, study, kind, round_, *, seat=None, route=None, receipt=None):
        if type(round_) is not int or not 1 <= round_ <= max(HORIZONS):
            raise ValueError("invalid round")
        if type(seat) is not int or not 0 <= seat < SEATS:
            raise ValueError("invalid seat")
        if kind not in ("open", "choose", "issue", "ack"):
            raise ValueError("invalid action")
        if kind == "choose" and route not in ("A", "B"):
            raise ValueError("invalid route")
        if kind == "ack" and (not isinstance(receipt, str) or not re.fullmatch(r"[a-f0-9]{32}", receipt)):
            raise ValueError("invalid receipt")
        with self.connect(write=True) as db:
            events = self.load(db, study)
            if not events:
                raise KeyError("unknown rehearsal")
            phase = next_state(events)
            name = {"open": "opportunity_opened", "choose": "choice_committed",
                    "issue": "settlement_issued", "ack": "settlement_acknowledged"}[kind]
            existing = next((e for e in events if e["type"] == name and e["round"] == round_), None)
            if existing is not None:
                same = existing["seat"] == seat
                same = same and (kind != "choose" or existing["route"] == route)
                same = same and (kind != "ack" or existing["receipt"] == receipt)
                if not same:
                    raise Conflict("retry differs from the recorded action")
                if kind == "issue" and phase["phase"] == "settlement":
                    return self.receipt_view(existing)
                return phase

            required = {"open": "handoff", "choose": "choice", "issue": "settlement", "ack": "settlement"}[kind]
            if (phase["phase"], phase.get("round"), phase.get("seat")) != (required, round_, seat):
                raise Conflict("action does not match the current phase, round and seat")
            setup, routes = from_events(events)
            previous = routes[seat]
            a = routes.count("A")
            if kind == "open":
                other = a - int(previous == "A")
                self.record(db, study, events, name, round_, seat=seat, previous=previous,
                            a=a, cost_A=other + 1, cost_B=2 * (SEATS - other))
            elif kind == "choose":
                after = a + int(route == "A") - int(previous == "A")
                self.record(db, study, events, name, round_, seat=seat, previous=previous,
                            route=route, before_A=a, after_A=after)
                if round_ == PAYOUT_ROUND:
                    # Draw only after the round-two choice has been recorded.
                    focal = setup["focal"]
                    focal_route = route if focal == seat else routes[focal]
                    self.record(db, study, events, "settlement_assigned", round_, seat=focal,
                                frame=self.rng.choice(FRAMES), amount=self.rng.choice(AMOUNTS),
                                route=focal_route, anchor_A=after)
            elif kind == "issue":
                assigned = events[-1]
                issued = self.record(db, study, events, name, round_, seat=seat,
                                     frame=assigned["frame"], amount=assigned["amount"],
                                     route=assigned["route"], receipt=secrets.token_hex(16))
                return self.receipt_view(issued)
            else:
                issued = events[-1]
                if issued["type"] != "settlement_issued" or not secrets.compare_digest(receipt, issued["receipt"]):
                    raise Conflict("the same seat must acknowledge an issued settlement")
                self.record(db, study, events, name, round_, seat=seat, receipt=receipt)
            return next_state(events)

    @staticmethod
    def receipt_view(event):
        return {k: event[k] for k in ("round", "seat", "frame", "amount", "route", "receipt")}

    def export(self, study):
        with self.connect() as db:
            events = self.load(db, study)
        if not events:
            raise KeyError("unknown rehearsal")
        if next_state(events)["phase"] != "complete":
            raise Conflict("finish the rehearsal before exporting")
        safe_events = [{k: v for k, v in event.items() if k != "receipt"} for event in events]
        return {"schema": PROTOCOL, "events": safe_events, "outcome": outcome(events)}
