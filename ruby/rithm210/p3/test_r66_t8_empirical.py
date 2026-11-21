import unittest
from r66_t8_empirical import aggregate_private,EPOCHS
class AggregateContractTests(unittest.TestCase):
    def test_synthetic_full_stability(self):
        groups={}
        for sid in range(1,25):
            for g in (1,2):
                for trt in (1,2,3,4):
                    info={i:int(trt==3 or trt==2 and i<3) for i in range(6)}
                    groups[sid,g,trt]={t:{i:(int(i<4),info[i]) for i in range(6)} for t in range(1,41)}
        x=aggregate_private(groups,draws=10)
        self.assertFalse(x['private_rows_exported'])
        for treatment in x['pooled_by_treatment_epoch'].values():
            for ep in EPOCHS:
                row=treatment[ep]
                self.assertEqual(row['old_A4_opportunities'],480)
                self.assertEqual(row['observed_stylized_recovery_excess'],0)
                self.assertEqual(row['point_id_interval_exact_fraction'],['0','0'])
