"""R36 source-free negative-control diagnostic contracts."""
import unittest
from r36_conditioning_sensitivity import partition,statistic,permutation_p

def rows():
    out=[]
    for s in (3,4):
        for i,(y,prev,v,yn) in enumerate(((1,0,6.,0),(1,1,9.,1),
                                          (1,1,13.,0),(0,1,7.,1),
                                          (0,0,12.,0),(0,0,15.,1))):
            out.append(dict(session=s,section=2,group=1,t=8,actor=i,
                            route=y,prior_route=prev,info=0,value=v,
                            already_decided=int(y!=prev),next_switch=int(y!=yn)))
    return out

class TestR36(unittest.TestCase):
    def test_conditioning_on_both_routes_determines_past_switch(self):
        c=partition(rows(),"both")
        self.assertTrue(all(len({z["already_decided"] for z in v})==1
                            for v in c.values()))
        self.assertAlmostEqual(statistic(c,"already_decided")[0],0.)
    def test_previous_only_does_not_force_current_switch(self):
        c=partition(rows(),"prior")
        self.assertTrue(any(len({z["already_decided"] for z in v})>1
                            for v in c.values()))
    def test_two_person_eligibility(self):
        c=partition(rows(),"current")
        self.assertEqual(sum(map(len,c.values())),12)
        self.assertTrue(all(len(v)>=2 for v in c.values()))
    def test_shuffles_reproducible(self):
        c=partition(rows(),"current")
        b,_=statistic(c,"next_switch")
        self.assertEqual(permutation_p(c,"next_switch",b,99,1),
                         permutation_p(c,"next_switch",b,99,1))
    def test_reject_unregistered_conditioning(self):
        with self.assertRaises(ValueError):partition(rows(),"post_value_payoff")

if __name__=="__main__":unittest.main()
