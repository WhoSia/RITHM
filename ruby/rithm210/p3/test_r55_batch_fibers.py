"""Source-free, exact brute-force checks of R55 six-person occupancy fibers."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import csv
import unittest

from r55_batch_fibers import (
    _session_bootstrap, analyze_rows, analyze_zip, fiber,
    uniform_label_kernel,
)


def masks_with(n):
    return [sum(1 << i for i in ix) for ix in combinations(range(6), n)]


def fake_rows():
    """Only artificial six-actor records; no authors' participant rows."""
    rows = []
    paths = {
        (1, 2): (0b001111, 0b001111, 0b001111),
        (2, 3): (0b001111, 0b010111, 0b010111),
        (3, 4): (0b001111, 0b111100, 0b111100),
    }
    for (arm, section), states in paths.items():
        for t, mask in enumerate(states, 1):
            n_a = mask.bit_count()
            previous = states[t-2] if t > 1 else mask
            gross = (mask ^ previous).bit_count()
            for actor in range(6):
                route_a = (mask >> actor) & 1
                row = {
                    "session": "3", "section": str(section), "trt": str(arm),
                    "Period": str(t), "ID": str(101 + actor), "Group": "1",
                    "RouteA": str(route_a), "RouteB": str(1-route_a),
                    "NumA": str(n_a), "NumB": str(6-n_a),
                    "Cost": str(n_a if route_a else 2*(6-n_a)),
                    "NumSwitch": str(gross),
                }
                rows.append(row)
    return rows


class R55ExactFiberTests(unittest.TestCase):
    def test_exhaustive_64_by_64_hamming_fiber_and_uniform_kernel(self):
        for a in range(7):
            for b in range(7):
                old = masks_with(a)
                new = masks_with(b)
                frequencies = Counter((x ^ y).bit_count() for x in old for y in new)
                self.assertEqual(tuple(sorted(frequencies)), fiber(a,b))
                expected = uniform_label_kernel(a,b)
                self.assertEqual(sum(expected.values()),1)
                for g, chance in expected.items():
                    self.assertEqual(chance, Fraction(frequencies[g],len(old)*len(new)))
                self.assertEqual(
                    sum(Fraction(g)*p for g,p in expected.items()),
                    Fraction(a*(6-b)+(6-a)*b,6),
                )

    def test_4_2_unchanged_has_three_latent_switch_counts(self):
        self.assertEqual(fiber(4,4),(0,2,4))
        self.assertEqual(uniform_label_kernel(4,4),
                         {0:Fraction(1,15),2:Fraction(8,15),4:Fraction(2,5)})
        old = 0b001111
        for new, expected in [(old,0),(0b010111,2),(0b111100,4)]:
            self.assertEqual(new.bit_count(),4)
            self.assertEqual((new ^ old).bit_count(),expected)
        self.assertEqual(fiber(0,6),(6,))
        self.assertEqual(fiber(3,3),(0,2,4,6))
        for invalid in [(-1,4),(1,7),(1.2,4),(True,2),(2,None)]:
            with self.assertRaises(ValueError):
                fiber(*invalid)

    def test_same_40_period_occupancy_path_can_have_156_extra_switches(self):
        # Two physically feasible histories with 4 A users in every period:
        # unchanged labels versus alternating two pairs of A and B actors.
        steady = [0b001111] * 40
        highly_mobile = [0b001111 if t % 2 == 0 else 0b111100
                         for t in range(40)]
        self.assertTrue(all(mask.bit_count() == 4 for mask in highly_mobile))
        self.assertEqual(sum((x ^ y).bit_count() for x, y in zip(steady,steady[1:])),0)
        self.assertEqual(sum((x ^ y).bit_count() for x, y in
                             zip(highly_mobile,highly_mobile[1:])),39*4)
        # Stage congestion welfare is identical; any strictly positive
        # switch cost would separate their total resource costs.
        self.assertEqual(sum(3*(x.bit_count()-4)**2 for x in steady),
                         sum(3*(x.bit_count()-4)**2 for x in highly_mobile))

    def test_fake_source_cost_and_identity_audits(self):
        source = fake_rows()
        result = analyze_rows(source, require_original=False, bootstrap_draws=20)
        self.assertEqual(result["population"]["group_period_transitions"],6)
        self.assertEqual(result["population"]["actor_decisions"],54)
        self.assertEqual(result["switches"]["observed_actor_changes"],6)
        self.assertEqual(result["switches"]["minimum_given_occupancy"],0)
        self.assertEqual(result["switches"]["extra_beyond_occupancy_minimum"],6)
        self.assertEqual(result["four_to_four_occupancy_fiber"]["observed_gross_count_distribution"],
                         {"0":4,"2":1,"4":1})
        corrupt = [dict(x) for x in source]
        corrupt[0]["Cost"] = "99"
        with self.assertRaisesRegex(ValueError,"cost mismatch"):
            analyze_rows(corrupt, require_original=False)
        with self.assertRaisesRegex(ValueError,"sealed 24-session"):
            analyze_rows(source,require_original=True)

    def test_rejects_fake_zip_as_original_before_reading(self):
        with TemporaryDirectory() as folder:
            zip_path = Path(folder)/"not_original.zip"
            with ZipFile(zip_path,"w") as z:
                z.writestr("data_task_all_switch_230705.csv","not a valid source")
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
                analyze_zip(zip_path)

    def test_weighted_whole_session_bootstrap_handles_unequal_sizes(self):
        # One group in session 1, three groups in session 2.
        from collections import Counter
        x = {}
        for s,n,diff in [(1,1,10),(2,3,-10)]:
            for arm in (1,2,3):
                row = Counter(group_sections=n)
                row["gross"] = diff if arm==3 else 0
                row["minimum"] = 0
                row["excess_pairs"] = 0
                row["congestion_excess"] = 0
                row["uniform_numerator"] = 0
                x[(s,arm)] = row
        r = _session_bootstrap(x,primary=1,secondary=3,draws=40,seed=1)
        self.assertEqual(r["metric_differences_per_group_section"]["gross"]
                         ["paired_pooled_difference_per_group_section"],0)
        # Equal-weighted per-session normalized differences would NOT yield
        # the pooled zero; session group counts 1 and 3 are essential.
        x[(2,3)]["gross"] = -3
        r = _session_bootstrap(x,primary=1,secondary=3,draws=40,seed=1)
        self.assertEqual(r["metric_differences_per_group_section"]["gross"]
                         ["paired_pooled_difference_per_group_section"],1.75)


if __name__=="__main__":
    unittest.main()
