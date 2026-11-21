"""R65 source-free synthetic checks; NEVER depend on approved participant ZIP."""
from collections import Counter
from pathlib import Path
import tempfile
import unittest
from r65_endogenous_stability import (load_private,transition_event,rate,
    epoch_counts,compare_epoch,bootstrap_paired)


def people(routes,info=None):
    if info is None: info=[0]*6
    return {i:(routes[i],info[i]) for i in range(6)}


def synthetic_groups():
    groups={}
    for sid in range(1,25):
        for group in (1,2):
            for trt in (1,2,3,4):
                info = [0]*6 if trt==1 else ([0]*3+[1]*3 if trt==2 else [1]*6)
                routes=[1,1,1,1,0,0]
                groups[(sid,group,trt)]={t:people(routes,info) for t in range(1,41)}
    return groups


class SourceFreeEndogenousTest(unittest.TestCase):
    def test_no_switch_versus_same_occupancy(self):
        a=people([1,1,1,1,0,0]);b=people([1,1,1,0,1,0])
        x=transition_event(a,b)
        self.assertEqual((x['a_before'],x['a_after'],x['up'],x['down']), (4,4,1,1))
        self.assertEqual((x['all_stay'],x['balanced_cancel']),(0,1))

    def test_unchanged_and_true_exit(self):
        a=people([1,1,1,1,0,0])
        self.assertEqual(transition_event(a,a)['all_stay'],1)
        b=people([1,1,1,0,0,0])
        self.assertEqual(transition_event(a,b)['a_after'],3)

    def test_reject_impossible_six_person_key(self):
        a=people([1,1,1,1,0,0]);b={0:(1,0)}
        with self.assertRaises(ValueError):transition_event(a,b)

    def test_zero_denominator_rejected(self):
        with self.assertRaises(ValueError):rate(Counter())

    def test_synthetic_horizon_and_full_census(self):
        agg,cluster,info,all6=epoch_counts(synthetic_groups())
        self.assertEqual(sum(info.values()),48)
        self.assertEqual(info[6],48)
        self.assertEqual(len(all6),48)
        summary=compare_epoch(agg)
        for trt in ('No','Partial','Full','Endogenous'):
            for ep in ('early','late'):
                self.assertEqual(summary[trt][ep]['transitions'],480)
                self.assertEqual(summary[trt][ep]['previous_A4'],480)
                self.assertEqual(summary[trt][ep]['P_all_stay_given_A4'],1)

    def test_paired_cluster_zero_on_identical_conditions(self):
        _,bycluster,_,_=epoch_counts(synthetic_groups())
        out=bootstrap_paired(bycluster,draws=30,seed=5)
        self.assertEqual(out['Endogenous_minus_Full_change']['delta'],0.)
        self.assertEqual(out['Endogenous_minus_Full_change']['descriptive_95'],[0.,0.])
        self.assertEqual(out['independent_sessions'],24)

    def test_wrong_shas_fail_before_zip_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wrong.zip';p.write_bytes(b'not an approved source')
            with self.assertRaisesRegex(ValueError,'SHA gate'):load_private(p)

    def test_after_period_t_is_not_predecision_state(self):
        a=people([1,1,1,1,0,0]);b=people([1,1,1,0,1,0])
        x=transition_event(a,b)
        self.assertEqual(x['a_before'],4)
        self.assertEqual(x['a_after'],4)
        self.assertNotEqual(x['all_stay'],1)

if __name__=='__main__':unittest.main()
