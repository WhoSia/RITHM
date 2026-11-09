import unittest
from r26_source_cv import training_shock_choice,projected,summarize
from r25_actor_calibration import fit

class TestR26SourceCV(unittest.TestCase):
    def train(self,truth=.5):
        groups=[]
        for session in range(1,21):
            for period in range(1,3):
                groups.append([dict(p=.5,y=int(i<3),prev=-1 if period==1 else int(i<3),
                     informed=1,period=period,session=session,group=1,
                     treatment=3) for i in range(6)])
        return groups
    def test_no_outer_fold_contamination_or_incomplete_train(self):
        groups=self.train()
        winner,values=training_shock_choice(groups,list(range(1,21)),'identity',
           shock_candidates=(('common',0.0),('common',.6)))
        self.assertIn(winner,values)
        self.assertEqual(2,len(values))
        with self.assertRaises(ValueError):training_shock_choice(groups,list(range(1,20)),'identity')
        outer=groups+[[dict(row,session=21,y=1) for row in groups[0]]]
        with self.assertRaises(ValueError):training_shock_choice(outer,list(range(1,21)),'identity')
    def test_pure_independence_output_keeps_individual_brier(self):
        groups=self.train()
        model=fit([r for g in groups for r in g],'identity')
        vals=projected(groups,model)
        self.assertEqual(40,len(vals))
        self.assertEqual(6,len(vals[0][0]))

if __name__=='__main__':unittest.main()

class TestR26Vectorized(unittest.TestCase):
    def test_vectorized_matches_direct_under_heterogeneous_probabilities(self):
        import random
        from r26_common_shock import candidates,forecast
        from r26_fast_batch import loglosses
        rng=random.Random(20261109)
        ps=[[rng.uniform(.02,.98) for _ in range(6)] for _ in range(101)]
        ys=[[rng.randrange(2) for _ in range(6)] for _ in range(101)]
        prev=[[rng.randrange(-1,2) for _ in range(6)] for _ in range(101)]
        for family,tau in candidates():
            actual=loglosses(ps,ys,prev,family,tau)
            expected=[forecast(p,tau,family,old).evaluate(y)['logloss']
                      for p,y,old in zip(ps,ys,prev)]
            for a,b in zip(actual,expected):
                self.assertAlmostEqual(a,b,places=11)


class TestR26EpochScope(unittest.TestCase):
    def test_equal_session_epoch_strata_without_retuning(self):
        from r26_source_cv import summarize
        rows=[]
        for sid in range(1,25):
            for period in (1,11,30):
                for treatment in (1,2,3):
                    for model in ('frequency','selected'):
                        row=dict(session=sid,period=period,treatment=treatment,model=model,
                                 baseline=dict(logloss=1.,joint_logloss=2.,brier=.5,cost_mae=3.,cost_bias=0.,actor_brier=.3),
                                 latent=dict(logloss=.9,joint_logloss=1.9,brier=.4,cost_mae=2.9,cost_bias=.1,actor_brier=.3))
                        rows.append(row)
        result=summarize(rows,[],list(range(1,25)),draws=10,groups=72)
        self.assertEqual(18,len(result['epoch_summaries']))
        for row in result['epoch_summaries']:
            self.assertEqual(24,row['groups'])
            self.assertAlmostEqual(-.1,row['logloss'])
        rows.pop()
        with self.assertRaises(ValueError):
            summarize(rows,[],list(range(1,25)),draws=10,groups=72)
