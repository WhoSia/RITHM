"""Offline contract tests only; no GitHub Actions / network / randomized p-hacking.
Invoke: python -m unittest -v test_rithm23_exact_bridge.py
"""
from decimal import Decimal, ROUND_HALF_UP
import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from rithm23_welfare_bridge import read_model_rounds, decomp, predicted_path_cost, predicted_social_cost

D=Path(__file__).parent
ROOT=D.parent # in standalone package the 2023 Ashraf author CSV is not bundled


class ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df,cls.rounds,cls.bad=read_model_rounds()

    def test_network_identity_all_integer_flows(self):
        for n1 in range(13):
            for n2 in range(13-n1):
                n3=12-n1-n2
                for shock in (0,1):
                    direct=(n1*predicted_path_cost(n1,n2,shock,1)
                           +n2*predicted_path_cost(n1,n2,shock,2)
                           +n3*predicted_path_cost(n1,n2,shock,3))
                    self.assertEqual(direct,predicted_social_cost(n1,n2,shock))

    def test_2017_archive_integrity(self):
        self.assertEqual(len(self.df),5760)
        self.assertEqual(len(self.rounds),480)
        self.assertEqual(len(self.bad),6)
        self.assertEqual(int((self.df.individual_error!=0).sum()),47)
        self.assertEqual(len(self.df.session.unique()),6)
        self.assertEqual(len(self.rounds.groupby(['session','group','stage'])),24)

    def test_2017_publication_rounded_exact(self):
        source=self.rounds.groupby('info').agg(structural=('structural','mean'),raw=('realized','mean'))
        self.assertAlmostEqual(source.loc[0,'structural'],210.62916666666666,places=10)
        self.assertAlmostEqual(source.loc[1,'structural'],219.1625,places=10)
        # 2017 PLOS ONE Table 5 prints 210.629 and 219.163.
        # Use exact integer sums and ROUND_HALF_UP rather than binary-float tie behavior.
        for k, expected in [(0, '210.629'), (1, '219.163')]:
            total=int(self.rounds.loc[self.rounds['info']==k,'structural'].sum())
            n=int((self.rounds['info']==k).sum())
            printed=(Decimal(total)/Decimal(n)).quantize(Decimal('.001'),rounding=ROUND_HALF_UP)
            self.assertEqual(str(printed),expected)

    def test_exact_variance_decomposition(self):
        for _,g in self.rounds.groupby(['info','z']):
            r=decomp(g)
            self.assertAlmostEqual(r['base_mean_flow']+r['network_dispersion']+r['shock_response_term'],r['total_structural_cost'])
        for _,g in self.rounds.groupby('info'):
            r=decomp(g)
            self.assertAlmostEqual(r['base_mean_flow']+r['network_dispersion']+r['shock_response_term'],r['total_structural_cost'])
        for _,g in self.rounds.groupby(['session','group','info']):
            r=decomp(g)
            self.assertAlmostEqual(r['base_mean_flow']+r['network_dispersion']+r['shock_response_term'],r['total_structural_cost'])

    def test_fixed_marginal_welfare_spread(self):
        # 12 identically distributed route 1 vs 3 travelers, P(route1)=1/2.
        # Different coupling: exactly balanced, iid, perfectly correlated.
        base=predicted_social_cost(6,0,0)
        self.assertEqual(base,192)
        self.assertEqual(base+2*0,192)
        self.assertEqual(base+2*3,198)
        self.assertEqual(base+2*36,264)

    def test_ashraf_2023_human_live_group_welfare(self):
        f=ROOT/'RITHM__2023__Ashraf_et_al__Aggregate_and_Individual_Effects_of_Information_in_a_Coordination_Traffic_Game__study1.csv'
        if not f.exists():self.skipTest('External personal-record source not bundled with GitHub')
        d=pd.read_csv(f)
        g=d.groupby(['Session','Period'],as_index=False).agg(profit=('Profit','sum'),n=('Subject','nunique'),n_side=('S','first'))
        self.assertEqual(len(g),1000)
        self.assertTrue((g.n==18).all())
        expected=-36+66*g.n_side-5*g.n_side*g.n_side
        self.assertTrue(np.array_equal(g.profit.to_numpy(),expected.to_numpy()))
        self.assertAlmostEqual(float(g.profit.mean()),160.126,places=3)


if __name__=='__main__': unittest.main()
