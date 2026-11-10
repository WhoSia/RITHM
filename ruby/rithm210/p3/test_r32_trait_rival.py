"""Source-free and private-hash-guarded tests for the R32 historical preference rival."""
import unittest
import tempfile
from pathlib import Path
from r32_trait_rival import design,previous_route_traits

class R32Tests(unittest.TestCase):
    def setUp(self):
        self.row=(1,4,7.,1,0)
        self.ctx=(1.,0.,.52,.38)
        self.trait=(.75,1.)
    def test_existing_r31_experience_nesting(self):
        from r31_order_history import design as old
        self.assertEqual(design(self.row,22,'experience',self.ctx,self.trait),
                         old(self.row,22,'prior_arm_experience',self.ctx))
    def test_no_current_or_future_outcome_can_enter_features(self):
        alt=(1,4,7.,1,1)
        for family in ('experience','preference','both'):
            self.assertEqual(design(self.row,22,family,self.ctx,self.trait),
                             design(alt,22,family,self.ctx,self.trait))
    def test_uninformed_actor_must_not_see_occupancy(self):
        row=(1,0,7.,0,0)
        altered=(1,6,7.,0,0)
        for family in ('experience','preference','both'):
            self.assertEqual(design(row,31,family,self.ctx,self.trait),
                             design(altered,31,family,self.ctx,self.trait))
    def test_trait_independent_of_payoff_experience_when_standalone(self):
        a=(1.,0.,.2,.1);b=(1.,0.,.8,.9)
        self.assertEqual(design(self.row,23,'preference',a,self.trait),
                         design(self.row,23,'preference',b,self.trait))
        self.assertNotEqual(design(self.row,23,'both',a,self.trait),
                            design(self.row,23,'both',b,self.trait))
    def test_historical_preference_matters_after_order_control(self):
        self.assertNotEqual(design(self.row,35,'preference',self.ctx,(.75,1.)),
                            design(self.row,35,'preference',self.ctx,(-.75,1.)))
    def test_first_segment_baseline_has_no_older_treatment(self):
        row=(0,3,-1.,0,1)
        self.assertEqual(design(row,2,'preference',(0.,0.,0.,0.),(0.,0.))[-2:], [0.,0.])
    def test_private_source_bytes_cannot_be_replaced(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)/'imposter.csv';fake.write_text('session,Group,ID,RouteA')
            with self.assertRaises(ValueError):
                from r31_order_history import prior_contexts
                prior_contexts(fake)
    def test_trait_invalid_outside_probability_domain(self):
        with self.assertRaises(ValueError):
            design(self.row,20,'preference',self.ctx,(3.,1.))
        with self.assertRaises(ValueError):
            design(self.row,20,'preference',self.ctx,(.2,3.))

if __name__=='__main__':unittest.main()
