"""RITHM R31 source-free invariants and optional private-source replay."""
from __future__ import annotations
import os,sys,unittest
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from r31_order_history import design,prior_contexts,session_metrics,run,FAMILIES

class TestR31(unittest.TestCase):
    def test_reuses_r30_without_extra_inputs(self):
        row=(1,2,7.,1,0)
        from r30_partial_dynamic_joint import design as original
        self.assertEqual(design(row,22,'r30_late',(0,1,3.,.5)),original(row,22,'payoff_public_late'))

    def test_source_legal_count_for_uninformed(self):
        for model in FAMILIES:
            for info in (0,):
                left=design((1,0,7.,info,0),30,model,(0,1,2.,.2))
                right=design((1,6,7.,info,1),30,model,(0,1,2.,.2))
                self.assertEqual(left,right)

    def test_future_outcome_never_in_design(self):
        for model in FAMILIES:
            a=design((0,4,5.,1,0),20,model,(1,0,3.,.1))
            b=design((0,4,5.,1,1),20,model,(1,0,3.,.1))
            self.assertEqual(a,b)

    def test_order_history_features_distinct(self):
        row=(0,3,4.,1,0)
        a=design(row,21,'prior_arm_order',(1,0,0.,0.))
        b=design(row,21,'prior_arm_order',(0,1,0.,0.))
        self.assertNotEqual(a,b)
        c=design(row,21,'prior_arm_experience',(1,0,1.,.2))
        d=design(row,21,'prior_arm_experience',(1,0,3.,.5))
        self.assertNotEqual(c,d)

    def test_vectorized_probabilities_against_independent_r30(self):
        from r30_partial_dynamic_joint import joint_scores
        p=np.array([.1,.25,.4,.51,.7,.8]);prior=np.array([1,0,1,0,0,1]);y=np.array([0,1,0,1,1,0])
        for tau in (0,.2,.4,.6):
            one=session_metrics([(p,prior,y)],tau)
            target=joint_scores(p,prior,y,tau)
            np.testing.assert_allclose(one,target,rtol=0,atol=1e-10)

    def test_expected_actor_group_sizes_and_no_hidden_source(self):
        self.assertRaises(ValueError,design,(0,3,4.,1,0),21,'wrong',(0,0,0.,0.))
        self.assertRaises(ValueError,design,(0,3,4.,1,0),21,'prior_arm_order',(0,2,0.,0.))

    @unittest.skipUnless(os.environ.get('RITHM_PRIVATE_SOURCE'), 'sealed author CSV not included in repository')
    def test_later_treatment_mutation_cannot_change_prior_context(self):
        import csv,hashlib,tempfile
        from unittest.mock import patch
        import r31_order_history as module
        p=Path(os.environ['RITHM_PRIVATE_SOURCE'])
        before,groups=prior_contexts(p)
        with p.open(newline='',encoding='utf-8-sig') as stream:
            rows=list(csv.DictReader(stream))
            fields=list(rows[0])
        # Pick a Part-I group whose Partial treatment was first (section2).
        first={(sid,g) for sid,glist in groups.items() for g in glist
               if any(int(r['session'])==sid and int(r['Group'])==g
                      and int(r['trt'])==2 and int(r['section'])==2
                      and int(r['Period'])==1 for r in rows)}
        self.assertTrue(first)
        sid,g=sorted(first)[0]
        later=next(r for r in rows if int(r['session'])==sid and int(r['Group'])==g
                   and int(r['trt']) in (1,3) and int(r['section'])>2)
        later['profit']=str(float(later['profit'])+1234.)
        with tempfile.TemporaryDirectory() as d:
            temporary=Path(d)/'future_treatment_tampered.csv'
            with temporary.open('w',newline='',encoding='utf-8-sig') as out:
                writer=csv.DictWriter(out,fieldnames=fields)
                writer.writeheader();writer.writerows(rows)
            changed_sha=hashlib.sha256(temporary.read_bytes()).hexdigest()
            with patch.object(module,'SOURCE_SHA',changed_sha):
                after,_=module.prior_contexts(temporary)
        self.assertEqual(before,after)

    @unittest.skipUnless(os.environ.get('RITHM_PRIVATE_SOURCE'), 'sealed author CSV not included in repository')
    def test_source_cohort_and_prepartial_contexts(self):
        path=os.environ['RITHM_PRIVATE_SOURCE']
        contexts,order=prior_contexts(path)
        self.assertEqual(len(contexts),288)
        self.assertEqual(sorted(len(v) for v in order.values()),[1]*4+[2]*16+[3]*4)
        self.assertEqual(sum(map(len,order.values())),48)
        from collections import Counter
        partial_sections=Counter()
        import csv
        with open(path,newline='',encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                if int(r['session']) in (2,101) or int(r['trt'])!=2 or int(r['Period'])!=1:continue
                partial_sections[int(r['section'])]+=1
        self.assertEqual(partial_sections,{2:96,3:96,4:96})
        # No prior treatment for section2; complete both arms for section4.
        for key,ctx in contexts.items():
            self.assertGreaterEqual(ctx[2],-5)
            self.assertTrue(0<=ctx[3]<=1)

if __name__=='__main__':unittest.main()
