import unittest
from r25_calibration_cv import event_rows,group_score,choose_calibration
from r25_actor_calibration import Calibrator

class TestR25CV(unittest.TestCase):
    def row(self,session,choice,actor=1):
        return dict(session=session,treatment=3,section=1,period=1,group=1,model='selected',
                    p=.5,y=choice,prev=-1,informed=1)

    def test_inner_cv_requires_20_sessions_and_never_passes_heldout(self):
        groups=[]
        for sid in range(1,21):
            for group in range(2):
                groups.append([self.row(sid,(sid+group+i)%2) for i in range(6)])
        choice,scores=choose_calibration(groups,list(range(1,21)))
        self.assertEqual(6,len(scores))
        self.assertIn(choice,scores)
        # Append arbitrary OUTER test sessions to an unrelated collection;
        # neither the fit records nor the chosen inner CV scores change.
        altered=groups+[[self.row(21,1) for i in range(6)]]
        choice2,scores2=choose_calibration([g for g in altered if g[0]['session']<=20],list(range(1,21)))
        self.assertEqual((choice,scores),(choice2,scores2))
        with self.assertRaises(ValueError):choose_calibration(groups,list(range(1,20)))

    def test_one_period_forecast_strictly_before_observed_update(self):
        groups={(1,1,1,1):[
            {'ID':str(i),'RouteA':str(int(i<=3)),'NumA':'3','trt':'3','Informed':'1'}
            for i in range(1,7)]}
        records=event_rows(groups,{(1,3):(1.,5.,.25)})
        self.assertEqual(2,len(records))
        for x in records:
            self.assertTrue(all(r['p']==.5 for r in x))
            self.assertTrue(all(r['prev']==-1 for r in x))
            result=group_score(x,Calibrator('identity',{}))
            self.assertAlmostEqual(31.5,result['predicted_cost'])
        groups[(1,1,1,1)][0]['NumA']='5'
        with self.assertRaises(ValueError):event_rows(groups,{(1,3):(1.,5.,.25)})

if __name__=='__main__':unittest.main()
