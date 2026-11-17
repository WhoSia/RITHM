import tempfile
import unittest
from pathlib import Path

from r44_store import ARMS, Conflict, Ledger


class OfferLedgerTests(unittest.TestCase):
    def test_balanced_roles_and_single_suggestion(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"r44.sqlite3"
            seen = set()
            for index in range(4):
                ledger = Ledger(path)
                key = f"{index:032x}"
                self.assertEqual(ledger.allocate(1, key), Ledger(path).allocate(1, key))
                first = ledger.view(key)["turn"]
                start = first["disclosed_A"]
                self.assertEqual(first["previous"], "A" if start == 5 else "B")
                suggested = first["suggestion"]
                if suggested:
                    self.assertNotEqual(suggested, first["previous"])
                seen.add((start, suggested is not None))
                # Both arms can stay with an identical first action.
                ledger.choose(key, 0, first["previous"], 10)
                ledger.choose(key, 0, first["previous"], 99)
                with self.assertRaises(Conflict):
                    ledger.choose(key, 0, "B" if first["previous"] == "A" else "A", 10)
                for step in range(1, 6):
                    turn = Ledger(path).view(key)["turn"]
                    self.assertIsNone(turn["suggestion"])
                    ledger.choose(key, step, turn["previous"], 10)
                saved = ledger.export(key)
                self.assertFalse(saved["first_seat_corrected"])
                self.assertIs(saved["events"][0]["followed_suggestion"], False if suggested else None)
                self.assertEqual(saved["events"][0]["response_ms"], 10)
                self.assertEqual(len({row["seat"] for row in saved["events"]}), 6)
            self.assertEqual(seen, set(ARMS))

    def test_accepted_offer_and_export(self):
        with tempfile.TemporaryDirectory() as folder:
            ledger = Ledger(Path(folder)/"r44.sqlite3")
            for _ in range(4):
                key = ledger.allocate(1)
                turn = ledger.view(key)["turn"]
                if turn["suggestion"] is None:
                    continue
                for step in range(6):
                    turn = ledger.view(key)["turn"]
                    ledger.choose(key, step, turn["suggestion"] or turn["previous"], 10)
                data = ledger.export(key)
                self.assertTrue(data["events"][0]["followed_suggestion"])
                self.assertTrue(data["first_seat_corrected"])
                self.assertEqual(data["summaries"][0]["first_target_turn"], 1)
                self.assertEqual(data["summaries"][0]["end_A"], 4)

    def test_http_reopen_after_choice(self):
        from json import dumps, load
        from threading import Thread
        from urllib.request import Request, urlopen
        from r44_server import server

        with tempfile.TemporaryDirectory() as folder:
            db_path = Path(folder)/"r44.sqlite3"
            key = "1"*32
            for reopen in (False, True):
                with server(Ledger(db_path), 0) as app:
                    worker = Thread(target=app.serve_forever)
                    worker.start()
                    root = f"http://127.0.0.1:{app.server_port}"
                    def api(path, data=None):
                        body = dumps(data).encode() if data is not None else None
                        req = Request(root+path, data=body, headers={"Content-Type":"application/json"})
                        with urlopen(req, timeout=3) as response:
                            return load(response)
                    try:
                        path = f"/group/{key}"
                        if not reopen:
                            self.assertEqual(api("/group", {"blocks": 1, "request_id": key})["id"], key)
                        for step in (range(1, 6) if reopen else range(1)):
                            turn = api(path)["turn"]
                            self.assertEqual(turn["step"], step)
                            api(path+"/choice", {"step": step, "route": turn["previous"], "response_ms": 10})
                        if reopen:
                            self.assertEqual(len(api(path+"/export")["events"]), 6)
                    finally:
                        app.shutdown()
                        worker.join()
