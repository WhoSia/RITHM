"""R28 exact six-person cost basis and source-privacy contracts."""
import unittest
from r28_fullinfo_cost_identification import route_cost,algebraic_cost,exact_enumeration

class R28IdentificationTests(unittest.TestCase):
    def test_all_feasible_person_route_states(self):
        checked=0
        for y in (0,1):
            for n in range(7):
                if (y==1 and n==0) or (y==0 and n==6):
                    continue
                self.assertEqual(route_cost(y,n),algebraic_cost(y,n))
                checked+=1
        self.assertEqual(checked,12)

    def test_null_direction_is_exact(self):
        # If logit has columns (1,y,n,y*n,c), the fifth is a
        # fixed linear combination of the first four. Coefficients
        # along the null direction do not change predictions.
        for y in (0,1):
            for n in range(7):
                if (y==1 and n==0) or (y==0 and n==6):continue
                x=(1,y,n,y*n,route_cost(y,n))
                null=(-12,12,2,-3,1)
                self.assertEqual(sum(a*b for a,b in zip(x,null)),0)

    def test_theorem_claim_is_no_more_than_collinearity(self):
        z=exact_enumeration()
        self.assertEqual(z["feasible_person_route_count_states"],12)
        self.assertEqual(z["rank_bound"],4)

    def test_impossible_person_histories_rejected(self):
        with self.assertRaises(ValueError):route_cost(1,0)
        with self.assertRaises(ValueError):route_cost(0,6)
        with self.assertRaises(ValueError):route_cost(2,4)
        with self.assertRaises(ValueError):route_cost(1,7)

if __name__=="__main__":unittest.main()
