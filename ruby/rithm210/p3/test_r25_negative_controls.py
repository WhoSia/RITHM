import math
import unittest
from r25_actor_calibration import fit
from r25_negative_controls import independent_exact,common_shock_exact,demo

class TestR25NegativeControls(unittest.TestCase):
    def test_exact_independent_wrong_probability(self):
        self.assertAlmostEqual(3.6,independent_exact([.7]*6,[.5]*6),places=10)
        self.assertAlmostEqual(0.,independent_exact([.7]*6,[.7]*6),places=10)

    def test_shared_shock_remains_after_perfect_marginal_calibration(self):
        self.assertAlmostEqual(22.5,common_shock_exact(),places=10)

    def test_train_only_global_fit_nearly_removes_spurious_pair_term(self):
        # Exactly balanced deterministic binomial proportions on TRAIN only;
        # test expectation uses the true independent .7 law, not fitted labels.
        row=dict(p=.5,prev=1,period=4,informed=1)
        train=[dict(row,y=1)]*7000+[dict(row,y=0)]*3000
        model=fit(train,'global')
        calibrated=model.probability(row)
        self.assertAlmostEqual(.7,calibrated,delta=.003)
        self.assertLess(abs(independent_exact([.7]*6,[calibrated]*6)),.002)

    def test_invalid_size_and_demo(self):
        with self.assertRaises(ValueError):independent_exact([.5]*5,[.5]*6)
        d=demo()
        self.assertEqual(3,set(d).__len__())
        self.assertAlmostEqual(3.6,d['independent_miscalibrated'])

if __name__=='__main__':unittest.main()
