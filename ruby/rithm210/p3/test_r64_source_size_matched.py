"""RITHM R64A source-free regression: exact actor-panel matching and leakage guards."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from r64_source_size_matched import (panel_key,source_panel_sample,fit_matched,
                                     prep_target,score_one_step,metrics)
from r63b_legal_bridge import load_private_events,predict


def fixture():
    out=[]
    for sid in (1,2,99):
        for trt in (1,2,3):
            for group in (0,1):
                for i in range(6):
                    info=0 if trt==1 else (1 if trt==3 else int(i>=3))
                    for t in range(2,41):
                        out.append({'session':sid,'section':3,'group':trt*10+group,
                          'actor':i,'period':t,'info':info,'treatment':trt,
                          'previous_route':int(i<4),'flip':int((i+t+group+sid)%6==0),
                          'prior_flips':3,'current_flips':(t-2)//6,'exposure':t-2,
                          'legal_bin':(t+i)%9})
    return out


class R64SourceSizeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=fixture()

    def test_panels_independent_of_outcomes(self):
        a=self.data[0]
        self.assertEqual(panel_key(a),panel_key({**a,'flip':1-a['flip']}))

    def test_exact_mask0_panel_match(self):
        chosen,meta=source_panel_sample(self.data,99,0,20261121)
        self.assertEqual(len(chosen),12)
        self.assertEqual(meta['source_panels_available'],24)
        self.assertEqual(meta['matched_source_panels'],meta['comparator_partial_panels'])
        self.assertTrue(all(s!=99 for s,sec,g,i in chosen))

    def test_exact_mask1_panel_match(self):
        chosen,meta=source_panel_sample(self.data,99,1,20261121)
        self.assertEqual(len(chosen),12)
        self.assertEqual(meta['source_panels_available'],24)
        self.assertTrue(all(g//10==3 for s,sec,g,i in chosen))

    def test_outcome_flip_does_not_change_selection(self):
        other=[{**e,'flip':1-e['flip']} for e in self.data]
        self.assertEqual(source_panel_sample(self.data,99,0,212)[0],
                         source_panel_sample(other,99,0,212)[0])

    def test_sample_seed_determinism_and_variation(self):
        a=source_panel_sample(self.data,99,0,212)[0]
        self.assertEqual(a,source_panel_sample(self.data,99,0,212)[0])
        self.assertNotEqual(a,source_panel_sample(self.data,99,0,213)[0])

    def test_full_39_period_panel_retention(self):
        fits,contract=fit_matched(self.data,99,20261121)
        for mask in (0,1):
            self.assertEqual(fits[mask]['n_source'],39*contract[mask]['matched_source_panels'])
            self.assertEqual(fits[mask]['source_masks'],(mask,))

    def test_holdout_original_session_absent_from_training(self):
        fits,_=fit_matched(self.data,99,20261121)
        alternate=[{**e,'flip':1-e['flip']} if e['session']==99 else e for e in self.data]
        other,_=fit_matched(alternate,99,20261121)
        self.assertEqual(fits,other)

    def test_reject_insufficient_source_support(self):
        reduced=[e for e in self.data if e['treatment']!=1 or e['session']==99 or e['actor']<2]
        with self.assertRaises(ValueError):
            source_panel_sample(reduced,99,0,1)

    def test_model_probabilities_open_and_mask_legal(self):
        fitted,_=fit_matched(self.data,99,20261121)
        for e in self.data:
            if e['session']==99 and e['treatment']==2:
                self.assertTrue(0<predict(e,fitted[e['info']])<1)

    def test_unapproved_zip_fails_before_parsing(self):
        with TemporaryDirectory() as t:
            p=Path(t,'bad.zip');p.write_bytes(b'not an authorized source')
            with self.assertRaisesRegex(ValueError,'SHA'):
                load_private_events(p)


if __name__=='__main__':unittest.main()
