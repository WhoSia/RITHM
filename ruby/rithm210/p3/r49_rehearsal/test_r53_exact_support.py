"""Independent tests: R53 exact discrete identified set vs its endpoint hull."""
from fractions import Fraction as Q
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from r49_store import Ledger
from r51_registry import registry
from r53_exact_support import compare_support, group_cost_support
from test_r49 import FixedDraws

CLOCK = (0,1,2,3,4)


class R53SupportTests(unittest.TestCase):
    def setUp(self):
        self.db = Path(self.enterContext(TemporaryDirectory()))/"test.sqlite"
        self.ledgers = {}

    def group(self, identifier, sign, *, move_at_three=False, through=4,
              last_choice=None):
        rng = FixedDraws(amount=sign)
        rng.clock = iter(CLOCK)
        ledger = Ledger(self.db, rng)
        key = f"{identifier:032x}"
        ledger.allocate(key, 5, 5)
        self.ledgers[identifier] = (ledger,key)
        while (phase := ledger.view(key))["phase"] != "complete":
            t, seat = phase["round"], phase["seat"]
            if t > through:
                break
            if phase["phase"] == "handoff":
                ledger.action(key,"open",t,seat=seat)
            elif phase["phase"] == "choice":
                value=phase["previous"]
                if t==3 and move_at_three:
                    assert seat==2
                    value="B"
                if t==5 and last_choice is not None:
                    value=last_choice
                ledger.action(key,"choose",t,seat=seat,route=value)
            else:
                ticket=ledger.action(key,"issue",t,seat=seat)
                ledger.action(key,"ack",t,seat=seat,receipt=ticket["receipt"])

    def bundle(self):
        return registry(Ledger(self.db))

    def test_strict_ranking_has_three_values_not_a_continuum(self):
        self.group(1,-4)
        self.group(2,+4,move_at_three=True)
        s = compare_support(self.bundle())
        c = s["comparisons"][0]
        self.assertEqual(c["attainable_cost_differences"],[Q(3),Q(6),Q(9)])
        self.assertEqual(c["bounds"],[Q(3),Q(9)])
        self.assertFalse(c["zero_is_attainable"])
        self.assertFalse(c["both_strict_signs_are_attainable"])
        half=compare_support(self.bundle(),metric="half_points")["comparisons"][0]
        self.assertEqual(half["attainable_cost_differences"],[Q(6),Q(12),Q(18)])

    def test_ambiguous_ranking_support_and_monotone_observation(self):
        self.group(1,-4)
        self.group(2,+4)
        c=compare_support(self.bundle())["comparisons"][0]
        self.assertEqual(c["attainable_cost_differences"],[Q(-3),Q(0),Q(3)])
        self.assertTrue(c["both_strict_signs_are_attainable"])
        self.assertTrue(c["zero_is_attainable"])
        self.group_existing_finish(1,"A")
        narrowed=compare_support(self.bundle())["comparisons"][0]
        self.assertEqual(narrowed["attainable_cost_differences"],[Q(0),Q(3)])
        self.group_existing_finish(2,"B")
        final=compare_support(self.bundle())["comparisons"][0]
        self.assertEqual(final["attainable_cost_differences"],[Q(3)])
        self.assertFalse(final["zero_is_attainable"])

    def group_existing_finish(self,identifier,last_choice):
        ledger,key=self.ledgers[identifier]
        while (p:=ledger.view(key))["phase"]!="complete":
            t,seat=p["round"],p["seat"]
            assert t==5 and seat==4
            if p["phase"]=="handoff":
                ledger.action(key,"open",t,seat=seat)
            else:
                ledger.action(key,"choose",t,seat=seat,route=last_choice)

    def test_exact_support_rejects_truncation_not_silent_approximation(self):
        self.group(1,-4)
        self.group(2,+4)
        bundle=self.bundle()
        with self.assertRaisesRegex(ValueError,"limit"):
            compare_support(bundle,max_values=1)
        with self.assertRaisesRegex(ValueError,"invalid"):
            compare_support(bundle,max_values=0)
        self.assertEqual(len(group_cost_support(bundle["cohort"][0]["events"])),2)


if __name__=="__main__":
    unittest.main()
