import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from r43_server import server
from r43_store import ARMS, Conflict, Ledger


class PilotTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name)/"test.sqlite3"
        self.ledger = Ledger(self.path)

    def test_allocation_survives_restarts_and_concurrent_requests(self):
        with ThreadPoolExecutor(6) as pool:
            ids = list(pool.map(self.ledger.allocate, [5]*12))
        with Ledger(self.path).connect() as db:
            states = [self.ledger.read(db, key)[0] for key in ids]
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual({(s["start"], s["signal"], s["marker"]) for s in states}, set(ARMS))
        self.assertEqual({s["allocation_batch"] for s in states}, {0})

    def test_same_allocation_key_does_not_consume_another_slot(self):
        key = "a"*32
        self.assertEqual(self.ledger.allocate(1, key), key)
        self.assertEqual(Ledger(self.path).allocate(1, key), key)
        with self.assertRaises(Conflict):
            self.ledger.allocate(5, key)
        with self.ledger.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM groups").fetchone()[0], 1)

    def test_transaction_retry_and_hidden_signal(self):
        key = self.ledger.allocate(1)
        for step in range(6):
            state = Ledger(self.path).view(key)
            self.assertEqual(state["turn"]["step"], step)
            self.assertNotIn("before_A", state["turn"])
            self.ledger.choose(key, step, "B", 20)
            self.ledger.choose(key, step, "B", 30)
            with self.assertRaises(Conflict):
                self.ledger.choose(key, step, "A", 20)
        saved = self.ledger.export(key)
        self.assertEqual(len({r["seat"] for r in saved["events"]}), 6)
        self.assertTrue(all(r["response_ms"] == 20 for r in saved["events"]))
        self.assertEqual(saved["summaries"][0]["end_A"], 0)
        self.assertEqual(saved["summaries"][0]["hit_then_lost"], saved["settings"]["start"] >= 4)
        for row in saved["events"]:
            disclosed = row["before_A"] if saved["settings"]["signal"] == "live" else saved["settings"]["start"]
            self.assertEqual(row["disclosed_A"], disclosed)

    def test_concurrent_different_actions_cannot_both_commit(self):
        key = self.ledger.allocate(1)

        def commit(route):
            try:
                self.ledger.choose(key, 0, route, 50)
            except Conflict:
                return "conflict"
            return route

        with ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(commit, ("A", "B")))
        self.assertEqual(outcomes.count("conflict"), 1)
        self.assertEqual(self.ledger.view(key)["turn"]["step"], 1)

    def test_http_allocate_resume_submit_export(self):
        def open_server():
            app = server(Ledger(self.path), 0)
            t = threading.Thread(target=app.serve_forever, daemon=True)
            t.start()
            self.addCleanup(app.server_close)
            self.addCleanup(app.shutdown)
            return app, f"http://127.0.0.1:{app.server_port}"

        app, base = open_server()

        def api(path, data=None):
            payload = None if data is None else json.dumps(data).encode()
            req = Request(base+path, data=payload, headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=3) as response:
                return json.load(response)

        with urlopen(base, timeout=3) as response:
            self.assertIn(b"rithm-r43-group", response.read())
        path = "/group/"+api("/group", {"blocks": 1})["id"]
        with self.assertRaises(HTTPError) as caught:
            api(path+"/export")
        self.assertEqual(caught.exception.code, 409)
        api(path+"/choice", {"step": 0, "route": "B", "response_ms": 100})
        app.shutdown()
        _, base = open_server()
        self.assertEqual(api(path)["turn"]["step"], 1)
        for step in range(1, 6):
            api(path+"/choice", {"step": step, "route": "B", "response_ms": 100})
        self.assertIsNone(api(path)["turn"])
        self.assertEqual(len(api(path+"/export")["events"]), 6)


if __name__ == "__main__":
    unittest.main()
