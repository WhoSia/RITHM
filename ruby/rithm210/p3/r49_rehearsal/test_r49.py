from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from r49_audit import audit
from r49_model import AMOUNTS, FRAMES
from r49_server import server
from r49_store import Conflict, Ledger

KEY = "1" * 32


class FixedDraws:
    """Independent fixed sequence for side-by-side dry-run cells."""

    def __init__(self, frame="route", amount=-4):
        self.frame, self.amount = frame, amount
        self.clock = iter((0, 1, 2, 0, 4) + tuple(range(6)) * 6)
        self.drawn = []

    def shuffle(self, routes):
        pass

    def choice(self, values):
        if values == FRAMES:
            self.drawn.append("frame")
            return self.frame
        if values == AMOUNTS:
            self.drawn.append("amount")
            return self.amount
        return values[0]

    def randrange(self, n):
        return next(self.clock)


def exercise(command, view, end_choice=None):
    """Complete a synthetic rehearsal, preserving each stage's normal API call."""
    while (phase := view())["phase"] != "complete":
        t, seat = phase["round"], phase["seat"]
        if phase["phase"] == "handoff":
            command("open", t, seat=seat)
        elif phase["phase"] == "choice":
            route = end_choice if t == 2 and end_choice else phase["previous"]
            command("choose", t, seat=seat, route=route)
        else:
            receipt = command("issue", t, seat=seat)
            command("ack", t, seat=seat, receipt=receipt["receipt"])


class RehearsalTests(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(tempfile.TemporaryDirectory())
        self.path = str(Path(temp) / "r49.sqlite3")
        self.rng = FixedDraws()
        self.ledger = Ledger(self.path, self.rng)
        self.ledger.allocate(KEY, 5, 5)

    def act(self, *args, **kwargs):
        return self.ledger.action(KEY, *args, **kwargs)

    def view(self):
        return self.ledger.view(KEY)

    def settle(self):
        for t, seat in ((1, 0), (2, 1)):
            self.act("open", t, seat=seat)
            self.act("choose", t, seat=seat, route="A")
        return self.act("issue", 2, seat=0)

    def test_treatment_draw_is_after_the_second_commit_and_hidden_in_view(self):
        self.act("open", 1, seat=0)
        self.act("choose", 1, seat=0, route="A")
        self.act("open", 2, seat=1)
        self.assertEqual(self.rng.drawn, [])
        with self.assertRaises(Conflict):
            self.act("issue", 2, seat=0)
        self.act("choose", 2, seat=1, route="B")
        self.assertEqual(self.rng.drawn, ["frame", "amount"])
        self.assertEqual(self.view(), {"phase": "settlement", "round": 2, "seat": 0})
        exercise(self.act, self.view)
        result = self.ledger.export(KEY)
        self.assertEqual(audit(result)["settlement_order"], (5, 6, 7, 8, 9))
        self.assertEqual(result["outcome"]["pre_settlement_A"], 4)
        self.assertEqual(result["outcome"]["first_focal_after_settlement"]["round"], 4)
        self.assertEqual(len(result["outcome"]["other_choices_before_focal"]), 1)

    def test_gate_rejects_early_open_wrong_seat_and_wrong_receipt(self):
        ticket = self.settle()
        with self.assertRaises(Conflict):
            self.act("open", 3, seat=2)
        with self.assertRaises(Conflict):
            self.act("ack", 2, seat=1, receipt=ticket["receipt"])
        with self.assertRaises(Conflict):
            self.act("ack", 2, seat=0, receipt="0"*32)
        with self.assertRaises(ValueError):
            self.act("ack", 2, seat=0, receipt="가")
        self.act("ack", 2, seat=0, receipt=ticket["receipt"])
        self.assertEqual(self.view()["round"], 3)
        self.assertNotIn("amount", self.act("issue", 2, seat=0))

    def test_restart_retries_and_conflicting_choices(self):
        ticket = self.settle()
        self.ledger = Ledger(self.path)
        self.ledger.allocate(KEY, 5, 5)
        self.assertEqual(self.act("issue", 2, seat=0), ticket)
        with self.assertRaises(Conflict):
            self.act("choose", 2, seat=1, route="B")
        self.act("choose", 2, seat=1, route="A")
        self.act("ack", 2, seat=0, receipt=ticket["receipt"])
        self.act("ack", 2, seat=0, receipt=ticket["receipt"])
        exercise(self.act, self.view)
        self.assertEqual(audit(self.ledger.export(KEY))["events"], 14)
        self.assertEqual(self.rng.drawn, ["frame", "amount"])

    def test_double_submit_cannot_draw_twice(self):
        self.act("open", 1, seat=0)
        self.act("choose", 1, seat=0, route="A")
        self.act("open", 2, seat=1)
        with ThreadPoolExecutor(2) as pool:
            results = [pool.submit(self.act, "choose", 2, seat=1, route="A") for _ in range(2)]
            self.assertTrue(all(f.result()["phase"] == "settlement" for f in results))
        self.assertEqual(self.rng.drawn, ["frame", "amount"])

    def test_partial_assignment_is_rolled_back_and_can_be_retried(self):
        self.act("open", 1, seat=0)
        self.act("choose", 1, seat=0, route="A")
        self.act("open", 2, seat=1)

        class FailingDraws(FixedDraws):
            def choice(self, values):
                if values == AMOUNTS:
                    raise RuntimeError("draw interrupted")
                return super().choice(values)

        self.ledger = Ledger(self.path, FailingDraws())
        with self.assertRaises(RuntimeError):
            self.act("choose", 2, seat=1, route="A")
        self.assertEqual(self.view()["phase"], "choice")
        self.ledger = Ledger(self.path, FixedDraws())
        self.act("choose", 2, seat=1, route="B")
        exercise(self.act, self.view)
        self.assertEqual(self.ledger.export(KEY)["outcome"]["pre_settlement_A"], 4)

    def test_no_focal_opportunity_is_censored_not_counted_as_staying(self):
        rng = FixedDraws()
        rng.clock = iter((0, 1, 2, 3, 4))
        ledger = Ledger(self.path, rng)
        study = "e"*32
        ledger.allocate(study, 5, 5)
        exercise(lambda *a, **k: ledger.action(study, *a, **k), lambda: ledger.view(study))
        result = ledger.export(study)["outcome"]
        self.assertIsNone(result["first_focal_after_settlement"])
        self.assertEqual(len(result["other_choices_before_focal"]), 3)

    def test_multicell_dry_run(self):
        for i, (start, frame, amount) in enumerate(product((4, 5), FRAMES, AMOUNTS), start=2):
            ledger = Ledger(self.path, FixedDraws(frame, amount))
            study = f"{i:032x}"
            ledger.allocate(study, start, 40)
            exercise(lambda *a, **k: ledger.action(study, *a, **k),
                     lambda: ledger.view(study))
            result = ledger.export(study)
            self.assertEqual(audit(result)["events"], 84)
            assigned = result["events"][5]
            self.assertEqual((assigned["frame"], assigned["amount"]), (frame, amount))
            self.assertNotIn("receipt", str(result))
            self.assertEqual(result["outcome"]["congestion_cost"], 120 if start == 5 else 0)

    def test_focal_route_is_post_commit_route_when_the_focal_acts(self):
        # For start=4 the focal seat is index 4, so use an explicit clock draw.
        rng = FixedDraws()
        rng.clock = iter((0, 4, 2, 4, 5))
        ledger = Ledger(self.path, rng)
        study = "f"*32
        ledger.allocate(study, 4, 5)
        exercise(lambda *a, **k: ledger.action(study, *a, **k), lambda: ledger.view(study), end_choice="A")
        result = ledger.export(study)
        self.assertEqual(result["events"][5]["route"], "A")
        self.assertEqual(result["outcome"]["first_exit_round"], 2)
        self.assertEqual(audit(result)["choices"], 5)

    def test_independent_audit_refuses_reordered_or_edited_events(self):
        exercise(self.act, self.view)
        report = self.ledger.export(KEY)
        wrong_order = deepcopy(report)
        wrong_order["events"][6:9] = reversed(wrong_order["events"][6:9])
        with self.assertRaises(ValueError):
            audit(wrong_order)
        report["events"][5]["route"] = "B"
        with self.assertRaises(ValueError):
            audit(report)

    def test_http_full_path_and_pending_exports(self):
        app = self.enterContext(server(self.ledger))
        thread = Thread(target=app.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join)
        self.addCleanup(app.shutdown)
        host = f"http://127.0.0.1:{app.server_port}"
        path = "/study/" + KEY

        def fetch(suffix, payload=None):
            data = None if payload is None else json.dumps(payload).encode()
            req = Request(host + suffix, data=data, headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=4) as response:
                return response.read()

        self.assertIn("6석 경로선택".encode(), fetch("/"))
        with self.assertRaises(HTTPError) as e:
            fetch(path + "/export")
        self.assertEqual(e.exception.code, 409)
        exercise(lambda kind, t, **body: json.loads(fetch(path + "/" + kind, {"round": t, **body})),
                 lambda: json.loads(fetch(path)))
        self.assertEqual(audit(json.loads(fetch(path + "/export")))["choices"], 5)


if __name__ == "__main__":
    unittest.main()
