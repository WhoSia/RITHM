from fractions import Fraction
import unittest

from r44_one_offer import first_block, net_saving


class OfferWelfareTests(unittest.TestCase):
    def test_pathwise_cost_difference(self):
        for n in range(6):
            self.assertEqual(net_saving(n, "B"), 3*((n+1-4)**2-(n-4)**2))
            self.assertEqual(net_saving(n, "A"), -net_saving(n, "B"))
        self.assertEqual(net_saving(Fraction(7, 2), "B"), 0)

    def test_dynamic_feedback_can_flip_sign(self):
        frozen = first_block(3, .6, 1., False)
        live = first_block(3, .6, 1., True)
        self.assertLess(frozen["saving_per_offer"], 0)
        self.assertGreater(live["saving_per_offer"], 0)
        for refresh in (False, True):
            self.assertEqual(first_block(5, .6, 0., refresh)["saving_per_offer"], 0)


class ObedienceTest(unittest.TestCase):
    def test_linear_program_agrees_with_analytic_thresholds(self):
        import json
        from pathlib import Path
        from r44_obedience import maximum_disutility

        path = Path(__file__).with_name("r43_results.json")
        table = json.loads(path.read_text())
        for n, exact in ((3, 1), (5, Fraction(97, 103))):
            result = maximum_disutility(table[str(n)]["marginals"], n)
            self.assertAlmostEqual(result["maximum_disutility"], float(exact))
            self.assertLessEqual(result["worst_obedience_constraint_error"], 1e-9)
