"""Local rehearsal ledger for one six-seat device per group."""
import json
import random
import secrets
import re
import sqlite3

from contextlib import closing, contextmanager
from itertools import product

ARMS = tuple(product((3, 4, 5), ("frozen", "live"), (False, True)))


class Conflict(ValueError):
    pass


class Ledger:
    def __init__(self, filename):
        self.filename = filename
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS groups "
                       "(id TEXT PRIMARY KEY, ordinal INTEGER UNIQUE, state TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events "
                       "(id TEXT, ordinal INTEGER, payload TEXT NOT NULL, "
                       "PRIMARY KEY(id, ordinal))")
            db.execute("CREATE TABLE IF NOT EXISTS design (key TEXT PRIMARY KEY, value TEXT)")
            db.execute("INSERT OR IGNORE INTO design VALUES ('seed', ?)", (secrets.token_hex(16),))

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.filename, timeout=10)) as db, db:
            yield db

    def allocate(self, blocks, request_id=None):
        if type(blocks) is not int or blocks not in (1, 5, 39):
            raise ValueError("invalid block count")
        if request_id is not None and (not isinstance(request_id, str)
                                       or not re.fullmatch(r"[a-f0-9]{32}", request_id)):
            raise ValueError("invalid allocation key")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if request_id is not None:
                existing = db.execute("SELECT state FROM groups WHERE id=?", (request_id,)).fetchone()
                if existing:
                    if json.loads(existing[0])["blocks"] != blocks:
                        raise Conflict("allocation key already used")
                    return request_id
            ordinal = db.execute("SELECT COUNT(*) FROM groups").fetchone()[0]
            seed = db.execute("SELECT value FROM design WHERE key='seed'").fetchone()[0]
            # Keep each rehearsal length in a separate randomized complete block sequence.
            within = db.execute("SELECT COUNT(*) FROM groups WHERE json_extract(state, '$.blocks')=?",
                                (blocks,)).fetchone()[0]
            batch, slot = divmod(within, len(ARMS))
            arms = list(ARMS)
            random.Random(f"{seed}/allocation/{blocks}/{batch}").shuffle(arms)
            start, signal, marker = arms[slot]
            group_id = request_id or secrets.token_hex(16)
            rng = random.Random(f"{seed}/seats/{ordinal}")
            initial = ["A"]*start+["B"]*(6-start)
            rng.shuffle(initial)
            orders = [rng.sample(range(6), 6) for _ in range(blocks)]
            state = dict(blocks=blocks, start=start, signal=signal, marker=marker,
                         initial=initial, orders=orders, allocation_batch=batch)
            db.execute("INSERT INTO groups VALUES (?, ?, ?)", (group_id, ordinal, json.dumps(state)))
        return group_id

    def read(self, db, group_id):
        row = db.execute("SELECT state FROM groups WHERE id=?", (group_id,)).fetchone()
        if row is None:
            raise KeyError("unknown group")
        events = db.execute("SELECT payload FROM events WHERE id=? ORDER BY ordinal",
                            (group_id,)).fetchall()
        return json.loads(row[0]), [json.loads(event[0]) for event in events]

    @staticmethod
    def next_turn(state, events):
        step = len(events)
        block, turn = divmod(step, 6)
        if block == state["blocks"]:
            return None
        routes = list(state["initial"])
        for event in events:
            routes[event["seat"]] = event["next"]
        seat = state["orders"][block][turn]
        current = routes.count("A")
        frozen = events[6*block]["before_A"] if turn else current
        signal = current if state["signal"] == "live" else frozen
        other = signal-int(routes[seat] == "A")
        return dict(step=step, block=block+1, turn=turn+1, seat=seat, previous=routes[seat],
                    disclosed_A=signal, before_A=current, cost_A=other+1, cost_B=2*(6-other))

    def view(self, group_id):
        with self.connect() as db:
            db.execute("BEGIN")
            state, events = self.read(db, group_id)
        turn = self.next_turn(state, events)
        if turn is not None:
            turn.pop("before_A")
        return dict(marker=state["marker"], blocks=state["blocks"], turn=turn)

    def choose(self, group_id, step, route, response_ms):
        if type(step) is not int or step < 0 or route not in ("A", "B"):
            raise ValueError("invalid action")
        if type(response_ms) is not int or not 0 <= response_ms <= 86_400_000:
            raise ValueError("invalid response time")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state, events = self.read(db, group_id)
            if step < len(events):
                if events[step]["next"] == route:
                    return  # Retried receipt, including retries after the final choice.
                raise Conflict("choice already recorded")
            turn = self.next_turn(state, events)
            if turn is None or turn["step"] != step:
                raise Conflict("turn is out of date")
            after = turn["before_A"]+int(route == "A")-int(turn["previous"] == "A")
            event = dict(turn, next=route, after_A=after, response_ms=response_ms)
            db.execute("INSERT INTO events VALUES (?, ?, ?)", (group_id, step, json.dumps(event)))

    def export(self, group_id):
        with self.connect() as db:
            db.execute("BEGIN")
            state, events = self.read(db, group_id)
        if len(events) != 6*state["blocks"]:
            raise Conflict("complete rehearsal before exporting")
        blocks = []
        for index in range(0, len(events), 6):
            rows = events[index:index+6]
            start, end = rows[0]["before_A"], rows[-1]["after_A"]
            first = 0 if start == 4 else next((r["turn"] for r in rows if r["after_A"] == 4), None)
            blocks.append(dict(block=rows[0]["block"], start_A=start, end_A=end,
                               first_target_turn=first, hit_then_lost=first is not None and end != 4,
                               excess_cost=3*(end-4)**2,
                               up=sum(r["previous"] == "B" and r["next"] == "A" for r in rows),
                               down=sum(r["previous"] == "A" and r["next"] == "B" for r in rows)))
        return dict(schema="rithm-r43-rehearsal-v1", group=group_id, settings=state,
                    events=events, summaries=blocks)
