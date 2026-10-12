"""P17 exact math contracts: no observational causal/welfare assumptions."""
import itertools
import random
import unittest
from rithm.phase_externality import Pair,phase_envelope,balanced_reallocation_proxy
from rithm.network_externality import (
    Edge,total_cost,atomic_reroute_delta,braess_model,braess_allocation,
    braess_exact_optimum,braess_greedy,route_latency,
    homogeneous_affine_dispersion)

class PhaseEnvelopeTests(unittest.TestCase):
    def test_p16_integer_witness(self):
        p=Pair(315,557,40.,80.)
        z=balanced_reallocation_proxy([p])
        self.assertEqual(z["minimum_nearflat_integer_reassignments"],121)
        self.assertAlmostEqual(z["nearflat_proxy"]-z["source_proxy"],1.5125)
        self.assertAlmostEqual(phase_envelope([p],global_budget=121)["max_proxy"],
                               z["nearflat_proxy"])
    def test_exhaustive_small_integer_oracle(self):
        r=random.Random(17026)
        for _ in range(140):
            p=[Pair(r.randint(0,6),r.randint(0,6),
                    r.choice([20.,30.,45.,70.]),r.choice([25.,50.,90.]))
               for i in range(3)]
            B=r.randint(0,7);cap=r.randint(0,4)
            z=phase_envelope(p,global_budget=B,per_pair_cap=cap)
            candidates=[]
            for xs in itertools.product(*[range(x.y0+x.y1+1) for x in p]):
                if sum(abs(x.y0-t) for x,t in zip(p,xs))>B:continue
                if any(abs(x.y0-t)>cap for x,t in zip(p,xs)):continue
                candidates.append(sum(t/x.speed0+(x.y0+x.y1-t)/x.speed1
                                      for x,t in zip(p,xs)))
            self.assertAlmostEqual(z["min_proxy"],min(candidates))
            self.assertAlmostEqual(z["max_proxy"],max(candidates))
    def test_bad_source_and_budgets(self):
        for args in ((-1,2,20,30),(3,1,0,20),(1,1,float("nan"),10)):
            with self.assertRaises(ValueError):Pair(*args)
        with self.assertRaises(ValueError):phase_envelope([],global_budget=1.5)
    def test_empty(self):
        z=phase_envelope([])
        self.assertEqual((z["min_proxy"],z["max_proxy"]),(0,0))

class MicroToMacroTests(unittest.TestCase):
    def test_braess_atomic_social_negative(self):
        e,p=braess_model()
        f,raw=braess_allocation({"upper":0,"lower":0,"shortcut":40},e,p)
        self.assertEqual(raw,3200)
        self.assertEqual(route_latency(e,f,p["shortcut"]),80)
        self.assertEqual(atomic_reroute_delta(e,f,p["shortcut"],p["upper"]),-34)
        self.assertEqual(route_latency(e,f,p["upper"]),85)
        self.assertEqual(braess_allocation({"upper":20,"lower":20,"shortcut":0})[1],2600)
        self.assertEqual(braess_exact_optimum()["cost"],2588)
        self.assertEqual(braess_greedy()["cost"],2588)
    def test_local_delta_exact_random(self):
        r=random.Random(111)
        edges={i:Edge(r.randint(1,15),r.random(),r.random()*.2)
               for i in range(35)}
        keys=list(edges)
        for _ in range(200):
            old=tuple(r.sample(keys,4));new=tuple(r.sample(keys,5))
            flows={k:r.randint(1,60) for k in keys}
            delta=atomic_reroute_delta(edges,flows,old,new)
            nextflows=flows.copy()
            for k in set(old)-set(new):nextflows[k]-=1
            for k in set(new)-set(old):nextflows[k]+=1
            self.assertAlmostEqual(total_cost(edges,nextflows)-total_cost(edges,flows),
                                   delta,places=5)
    def test_greedy_never_below_enumerated(self):
        for n in range(1,22):
            exact=braess_exact_optimum(n);greedy=braess_greedy(n)
            self.assertGreaterEqual(greedy["cost"],exact["cost"])
            self.assertLessEqual(greedy["accepted_moves"],3*n)
    def test_affine_dispersion_identity(self):
        a=homogeneous_affine_dispersion([20,20],free=10,slope=2)
        b=homogeneous_affine_dispersion([0,40],free=10,slope=2)
        self.assertEqual(b["dispersion_surcharge"]-a["dispersion_surcharge"],1600)
        self.assertEqual(b["system_cost"]-a["system_cost"],1600)
    def test_affine_dispersion_random(self):
        r=random.Random(1977)
        for n in range(1,51):
            f=[r.randint(0,300) for _ in range(n)]
            z=homogeneous_affine_dispersion(f,free=.1,slope=.35)
            self.assertAlmostEqual(z["system_cost"],
                z["homogeneous_reference"]+z["dispersion_surcharge"],places=6)
