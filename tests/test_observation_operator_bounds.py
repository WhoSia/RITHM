"""Formal source-independent P16 math contracts: no causal instrument claim."""
import unittest
from itertools import product
from rithm.observation import minimal_balancing_transfer, feasible_latent_first_bin


class OperatorIdentificationTests(unittest.TestCase):
    def test_original_p15_witness(self):
        self.assertEqual(minimal_balancing_transfer(315, 557), 121)
        self.assertEqual(feasible_latent_first_bin(315, 557)["range"], [0, 872])

    def test_integer_lower_bound_exhaustive(self):
        for a,b in product(range(13),repeat=2):
            t=a+b
            allowed=[x for x in range(t+1) if abs(x-(t-x))<=1]
            self.assertEqual(min(abs(a-x) for x in allowed),
                             minimal_balancing_transfer(a,b))

    def test_cocoverage_reference_discriminates(self):
        x=feasible_latent_first_bin(315,557,reference_even=436,
                  reference_odd=436,reference_error_bound=4)
        self.assertEqual(x["range"],[432,440])
        self.assertTrue(x["near_flat_compatible"])
        self.assertFalse(x["source_faithful_compatible"])

    def test_small_source_error_budget_rejects_flat(self):
        a=feasible_latent_first_bin(315,557,source_error_bound=100)
        b=feasible_latent_first_bin(315,557,source_error_bound=121)
        self.assertFalse(a["near_flat_compatible"])
        self.assertTrue(b["near_flat_compatible"])

    def test_incompatible_sources(self):
        x=feasible_latent_first_bin(315,557,source_error_bound=2,
               reference_even=436,reference_odd=436,reference_error_bound=2)
        self.assertFalse(x["compatible"])

    def test_invalid_negative_missing_one_reading(self):
        for a,b in ((-1,5),(1.5,7),(1,-2)):
            with self.assertRaises(ValueError): minimal_balancing_transfer(a,b)
        with self.assertRaises(ValueError):
            feasible_latent_first_bin(2,3,reference_even=3)
        with self.assertRaises(ValueError):
            feasible_latent_first_bin(2,3,reference_even=3,reference_odd=2,reference_error_bound=-1)
