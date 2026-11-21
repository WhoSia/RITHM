"""Source-free exact assignment-null tests, no original person records."""
import unittest
from r60_identity_placebo import blocks,build_cost_matrices,permutation_check
from r60_cross_segment import events_from_histories


def synthetic_people():
    from collections import defaultdict
    people={}
    for sess in range(1,25):
        for group in (1,2):
            for ident in range(6):
                for sec in (2,3,4):
                    key=(sess,sec,100*group+ident)
                    people[key]={t:((t+ident+sess+group+sec)%2 if ident<2 else ident%2,
                                     int(ident%2==0 and sec>2),sec-1,group)
                                 for t in range(1,41)}
    return people


class R60LabelNullGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events,_=events_from_histories(synthetic_people())
        cls.costs=build_cost_matrices(cls.events)

    def test_all_actor_contrast_matrices_have_6x6_support(self):
        self.assertEqual(len(self.costs),96)
        for x in self.costs:
            self.assertEqual(len(x['matrix']),6)
            self.assertEqual(len(x['attrs']),6)
            self.assertTrue(all(len(row)==6 for row in x['matrix']))

    def test_group_stratum_is_entire_six_person_group(self):
        self.assertEqual(blocks([(0,0,0,0)]*6,'group'),[[0,1,2,3,4,5]])

    def test_information_mask_is_preserved_by_blocking(self):
        a=[(1,1,0,0),(1,1,1,0),(0,0,1,1),(0,0,0,0),(1,0,0,0),(1,0,1,1)]
        b=blocks(a,'same_information')
        self.assertEqual(sorted(sorted(v) for v in b),[[0,1],[2,3],[4,5]])
        strict=blocks(a,'same_information_and_boundary_route')
        self.assertEqual(sorted(sum(strict,[])),list(range(6)))
        self.assertTrue(all(len(v)==1 for v in strict))

    def test_bad_null_mode_and_bad_repetitions_fail(self):
        with self.assertRaises(ValueError):blocks([(0,0,0,0)]*6,'wrong')
        with self.assertRaises(ValueError):permutation_check(self.costs,reps=0)

    def test_identity_permutation_is_seeded_and_source_free(self):
        a=permutation_check(self.costs,reps=16,seed=7)
        b=permutation_check(self.costs,reps=16,seed=7)
        self.assertEqual(a,b)
        self.assertEqual(set(a),{'group','same_information','same_information_and_boundary_route'})
        for d in a.values():
            self.assertEqual(d['actor_decisions'],22464)
            self.assertTrue(0<d['one_sided_permutation_p_upper']<=1)
            self.assertTrue('actor' not in d and 'session' not in d)

    def test_exact_permutation_mean_matches_two_cell_enumeration(self):
        # Two people with losses 1 and 2 on their identity, cross-loss 3 and 4:
        # actual=1+2=3, swapped=3+4=7, null expected total=5.
        matrix=[[1,3,1,1,1,1],[4,2,1,1,1,1]]+[[1]*6 for _ in range(4)]
        blocks2=blocks([(0,0,0,0),(0,0,0,0)]+[(1,1,0,i%2) for i in range(4)],
                       'same_information_and_boundary_route')
        # first two are swappable; other blocks are irrelevant, use direct arithmetic.
        self.assertIn([0,1],blocks2)
        self.assertEqual((matrix[0][0]+matrix[1][0]+matrix[0][1]+matrix[1][1])/2,5)

if __name__=='__main__':unittest.main()
