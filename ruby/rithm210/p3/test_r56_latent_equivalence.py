"""R56 fixed-size falsifier with exact probabilities over all 64 old masks."""
import unittest
from fractions import Fraction
from r56_latent_equivalence import coordinated_pair_swap,latent_common_instruction


class R56LatentMechanismTests(unittest.TestCase):
    def test_two_different_latent_stories_have_identical_full_labelled_kernel(self):
        for start in range(64):
            coordinated=coordinated_pair_swap(start)
            independent_given_H=latent_common_instruction(start)
            self.assertEqual(coordinated,independent_given_H)
            self.assertEqual(sum(coordinated.values()),1)
            self.assertTrue(all(n.bit_count()==start.bit_count() for n in coordinated))
            self.assertTrue(all((start^n).bit_count()==(0 if start in (0,63) else 2)
                                for n in coordinated))
    def test_all_eight_opposite_pair_swaps_at_four_two(self):
        law=coordinated_pair_swap(0b001111)
        self.assertEqual(len(law),8)
        self.assertEqual(set(law.values()),{Fraction(1,8)})
    def test_reject_illegal_labelled_masks(self):
        with self.assertRaises(ValueError):coordinated_pair_swap(64)
        with self.assertRaises(ValueError):latent_common_instruction(-1)


if __name__=='__main__':unittest.main()
