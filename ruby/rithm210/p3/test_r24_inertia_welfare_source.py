import unittest
from r23_inertia_memory_cv import candidates,label
from r24_inertia_welfare_source import trained_choices,residual_rows,summaries

class TestR24WelfareSource(unittest.TestCase):
    def test_18_fold_winners_ignore_own_heldout_outcome(self):
        names=[label(c) for c in candidates()]
        rows=[dict(session=s,treatment=t,model=name,
                   logloss=.2 if name==names[0] else 1.)
              for s in range(1,25) for t in (1,2,3) for name in names]
        choices,folds=trained_choices(dict(session_results=rows))
        self.assertEqual(72,len(choices))
        self.assertEqual(18,len(folds))
        self.assertTrue(all(f['training_sessions']==20 and
                            f['heldout_sessions']==4 for f in folds))
        for row in rows:
            if (row['session']-1)%6==0:
                row['logloss'] = -100. if row['model']==names[-1] else 100.
        _,modified=trained_choices(dict(session_results=rows))
        self.assertEqual([r for r in folds if r['fold']==0],
                         [r for r in modified if r['fold']==0])

    def test_full_six_person_two_period_trace_and_unknown_first_cohort(self):
        source={}
        for t in (1,2):
            source[(1,1,t,1)]=[
                {'ID':str(i),'RouteA':str(int(i<=3)),
                 'NumA':'3','trt':'3'} for i in range(1,7)]
        options={(1,3):(1.,5.,.25)}
        rows=residual_rows(source,options)
        self.assertEqual(4,len(rows))
        initial=[r for r in rows if r['period']==1]
        self.assertTrue(all(r['same_pair']==0 and
                            r['opposite_pair']==0 for r in initial))
        self.assertTrue(all(abs(r['welfare_error']-r['linear']-
                  r['diagonal']-r['same_pair']-r['opposite_pair']-
                  r['unknown_pair'])<1e-9 for r in rows))
        source[(1,1,2,1)][0]['NumA']='6'
        with self.assertRaises(ValueError):
            residual_rows(source,options)

    def test_missing_sessions_rejected(self):
        with self.assertRaises(ValueError):
            summaries([],draws=100)

if __name__=='__main__':unittest.main()
