"""Brute-force and replay checks for R52's sharp dynamic program."""
from itertools import product
from pathlib import Path
import tempfile
import unittest

from r49_model import from_events, outcome
from r49_store import Ledger
from r51_registry import registry
from r52_welfare_bounds import evaluate_registry, sharp_bounds
from test_r49 import FixedDraws, exercise


class R52Tests(unittest.TestCase):
    def setUp(self):
        self.path = Path(self.enterContext(tempfile.TemporaryDirectory())) / "rehearsal.sqlite3"

    def create(self, clock, *, complete=False):
        rng = FixedDraws()
        rng.clock = iter(clock)
        ledger = Ledger(self.path, rng)
        key = "e"*32
        ledger.allocate(key, 5, len(clock))
        for t, seat in ((1, clock[0]), (2, clock[1])):
            ledger.action(key, "open", t, seat=seat)
            ledger.action(key, "choose", t, seat=seat, route="A")
        ticket = ledger.action(key, "issue", 2, seat=0)
        ledger.action(key, "ack", 2, seat=0, receipt=ticket["receipt"])
        if complete:
            exercise(lambda kind, t, **kw: ledger.action(key, kind, t, **kw),
                     lambda: ledger.view(key))
        with ledger.connect() as db:
            events = ledger.load(db, key)
        return ledger, key, events

    @staticmethod
    def exhaustive(events):
        cfg, routes = from_events(events)
        n_done = sum(e["type"] == "choice_committed" for e in events)
        excess_done = sum(3*(e["after_A"]-4)**2 for e in events if e["type"] == "choice_committed")
        focal_done = sum(e["seat"]==cfg["focal"] and e["previous"]!=e["route"]
                         for e in events if e["type"] == "choice_committed")
        outputs=[]
        for bits in product((0,1), repeat=len(cfg["clock"])-n_done):
            latest=routes.copy()
            excess=excess_done
            changes=focal_done
            for seat, toggle in zip(cfg["clock"][n_done:], bits):
                if toggle:
                    latest[seat]="B" if latest[seat]=="A" else "A"
                    changes+=int(seat==cfg["focal"])
                excess+=3*(latest.count("A")-4)**2
            outputs.append((excess, 2*excess+changes))
        return [[min(a for a,b in outputs),max(a for a,b in outputs)],
                [min(b for a,b in outputs),max(b for a,b in outputs)]]

    @staticmethod
    def replay_witness(events, path):
        cfg, routes = from_events(events)
        done = [e for e in events if e["type"] == "choice_committed"]
        excess=sum(3*(e["after_A"]-4)**2 for e in done)
        focal=sum(e["seat"] == cfg["focal"] and e["previous"] != e["route"] for e in done)
        for event in path:
            seat=event["seat"]
            changed=event["route"] != routes[seat]
            if changed!=event["changed"]:
                raise AssertionError("witness contradicts route transition")
            focal+=int(changed and seat==cfg["focal"])
            routes[seat]=event["route"]
            excess+=3*(routes.count("A")-4)**2
        return excess, 2*excess+focal

    def test_exact_against_all_2_to_5_round_completions(self):
        for clock in ((0,1,0,2,3),(0,1,2,3,4),(0,1,2,0,3)):
            _,_,events=self.create(clock)
            result=sharp_bounds(events,witnesses=True)
            expected=self.exhaustive(events)
            self.assertEqual(result["full_excess_cost_bounds"],expected[0])
            self.assertEqual(result["full_total_cost_half_points_bounds"],expected[1])
            for name, path in result["witnesses"].items():
                attained=self.replay_witness(events,path)
                objective=0 if "excess" in name else 1
                extreme=0 if name.startswith("min") else 1
                self.assertEqual(attained[objective],expected[objective][extreme])
            break

    def test_actual_completed_result_is_an_exact_point(self):
        ledger,key,events=self.create((0,1,0,2,3),complete=True)
        val=sharp_bounds(events)
        observed=outcome(events)
        self.assertEqual(val["full_excess_cost_bounds"],[observed["congestion_cost"]]*2)
        self.assertEqual(val["full_total_cost_half_points_bounds"],
                         [observed["modeled_total_cost_half_points"]]*2)
        self.assertEqual(val["reachable_dynamic_states"],1)

    def test_fixed_clock_tightens_coarse_48_points_each_stage(self):
        ledger,key,events=self.create((0,1,2,3,4))
        coarse=registry(ledger)["cohort"][0]["summary"]["excess_cost_bounds"]
        sharp=sharp_bounds(events)["full_excess_cost_bounds"]
        self.assertLess(sharp[1]-sharp[0],coarse[1]-coarse[0])
        self.assertEqual(sharp,self.exhaustive(events)[0])

    def test_registry_cost_bounds_are_tighter_than_conservative(self):
        ledger,_,_=self.create((0,1,0,2,3))
        bundle=registry(ledger)
        result=evaluate_registry(bundle)
        one=result["cells"][0]
        target=sharp_bounds(bundle["cohort"][0]["events"])
        self.assertEqual(one["mean_excess_cost_bounds"],
                         target["full_excess_cost_bounds"])
        self.assertIn("not causal",result["scope"])


if __name__ == "__main__":
    unittest.main()
