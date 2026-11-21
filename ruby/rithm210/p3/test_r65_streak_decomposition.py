"""Source-free stability-spell decomposition tests without human source."""
from collections import Counter,defaultdict
import unittest
from r65_streak_decomposition import chronological_streak_counts,symmetric_decomposition,resampling
from test_r65_endogenous_stability import synthetic_groups

class StreakDecompositionTest(unittest.TestCase):
    def test_streak_metrics_on_static_synthetic_configuration(self):
        x=chronological_streak_counts(synthetic_groups(),3)
        sessions=list(range(1,25))
        # The late source has no age-one rows: explicitly refuse an invented rate.
        with self.assertRaisesRegex(ValueError,'age-bin outcome'):
            symmetric_decomposition(x,sessions,coarse=True)

    def test_alternative_bins_change_attribution_without_changing_total(self):
        d=defaultdict(Counter)
        for sid in range(1,25):
            for ep,bin,stay,n in [('early','1',2,10),('early','2',2,5),('early','3-4',2,5),('early','5+',3,5),
                                  ('late','1',4,5),('late','2',3,5),('late','3-4',5,5),('late','5+',10,20)]:
                d[sid,ep,bin].update({'n':n,'stay':stay})
        a=symmetric_decomposition(d,list(range(1,25)),coarse=False)
        b=symmetric_decomposition(d,list(range(1,25)),coarse=True)
        self.assertAlmostEqual(a['total_change'],b['total_change'])
        self.assertNotAlmostEqual(a['composition'],b['composition'])
        self.assertAlmostEqual(a['composition']+a['within_age_bin'],a['total_change'])
        self.assertAlmostEqual(b['composition']+b['within_age_bin'],b['total_change'])

    def test_bootstrap_preserves_original_session_unit(self):
        d=defaultdict(Counter)
        for sid in range(1,25):
            for ep in ('early','late'):
                for b in ('1','2'):
                    d[sid,ep,b].update({'n':5,'stay':2})
        bs=resampling(d,list(range(1,25)),draws=30,seed=22)
        self.assertEqual(bs['valid'],30)
        self.assertEqual(bs['composition']['descriptive_95'],[0.,0.])

    def test_horizon_periods_exclude_off_by_one(self):
        x=chronological_streak_counts(synthetic_groups(),4)
        self.assertEqual(sum(x[s,'early',b]['n'] for s in range(1,25) for b in ('1','2','3-4','5+')),480)
        self.assertEqual(sum(x[s,'late','5+']['n'] for s in range(1,25)),480)

    def test_reject_wrong_original_treatment(self):
        with self.assertRaises(ValueError):chronological_streak_counts({},1)

if __name__=='__main__':unittest.main()
