import unittest
from copy import deepcopy
from random import Random
from statistics import mean
import numpy as np
from r62_batch import batch_law,full_cv_fast
from r62_collective import fast_group_proba,FROZEN,GRID,aggregate,pause_parameter


def artificial_sessions():
    events=[]
    for s in range(1,25):
        for group in (1,2):
            routes=[1,1,1,1,0,0];counts=[0]*6
            for t in range(2,6):
                for i in range(6):
                    y=int((i+s+group+t)%7==0)
                    events.append({'session':s,'section':3,'group':group,'period':t,'actor':i,
                        'treatment':((s+group)%3)+1,'info':int((s+group)%3!=0),
                        'previous_route':routes[i],'flip':y,'own_count':(s+i)%10,
                        'current_count':counts[i], 'current_exposure':t-2})
                    counts[i]+=y
                    routes[i]^=y
    return events

class SourceFreeBatch(unittest.TestCase):
    def test_vectorized_fast_equals_scalar_all_mask_supports(self):
        rng=Random(621)
        for n in (1,17,40):
            old=np.array([[rng.randrange(2) for _ in range(6)] for _ in range(n)])
            ps=np.array([[rng.uniform(.05,.65) for _ in range(6)] for _ in range(n)])
            periods=np.array([rng.randrange(2,41) for _ in range(n)])
            u=np.array([rng.randrange(7-int(x.sum())) for x in old]);d=np.array([rng.randrange(int(x.sum())+1) for x in old])
            for model in FROZEN:
                for q in (0,.15,.35):
                    target,pzero=batch_law(old,ps,u,d,periods,model,q)
                    for i in range(n):
                        a,b=fast_group_proba(old[i].tolist(),ps[i].tolist(),int(u[i]),int(d[i]),model,q,int(periods[i]))
                        self.assertAlmostEqual(target[i],a,places=11)
                        self.assertAlmostEqual(pzero[i],b,places=11)

    def test_probability_capacity_clipping_is_safe(self):
        high=[.92,.8,.3,.23,.2,.1]
        q=pause_parameter(.4,'pause_at_four',4,30,high)
        self.assertTrue(0<q<1-max(high))
        self.assertEqual(pause_parameter(.4,'pause_at_four',3,30,high),0)
        self.assertEqual(pause_parameter(.4,'pause_late_four',4,10,high),0)

    def test_evaluation_excludes_heldout_session_in_train_q(self):
        events=artificial_sessions()
        _,selected=full_cv_fast(events)
        changed=deepcopy(events)
        for e in changed:
            if e['session']==1:e['flip']=1-e['flip']
        _,after=full_cv_fast(changed)
        for m in selected:
            self.assertEqual(selected[m][0],after[m][0])

    def test_outer_nested_selector_does_not_use_heldout(self):
        events=artificial_sessions()
        r,s=full_cv_fast(events,actor_model='nested_adaptive')
        self.assertEqual(len(r['independent']),24)
        self.assertEqual(len(s['pause_at_four']),24)

    def test_each_original_group_emits_six_synthetic_labels(self):
        events=artificial_sessions()
        result,select=full_cv_fast(events)
        a=aggregate(result,select,bootstrap=50)
        self.assertEqual(a['cohort']['sessions'],24)
        self.assertEqual(a['cohort']['individual_decisions'],24*2*4*6)
        self.assertEqual(a['cohort']['group_transitions'],24*2*4)

    def test_invalid_synthetic_population_fails_closed(self):
        with self.assertRaises(ValueError):full_cv_fast(artificial_sessions()[:20])

    def test_all_zero_pause_gate_reduces_to_independent(self):
        old=np.array([[1,1,1,1,0,0]]);p=np.array([[.2,.1,.3,.3,.4,.2]])
        u=np.array([0]);d=np.array([0]);t=np.array([35])
        a=batch_law(old,p,u,d,t,'pause_at_four',0)
        b=batch_law(old,p,u,d,t,'independent',0)
        for aa,bb in zip(a,b):self.assertAlmostEqual(aa[0],bb[0])

if __name__=='__main__':unittest.main()
