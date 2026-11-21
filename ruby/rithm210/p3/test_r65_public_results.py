"""Source-free R65 public scientific-result SHA and interpretation contracts."""
from hashlib import sha1
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
BLOBS={
 'r65_endogenous_aggregate.json':'878c3526963b96db5434d65c66f943b2330d6eb0',
 'r65_ssm_fitted_aggregate.json':'6d32c56f965334107d4e576a5ef25615932f465e',
 'r65_streak_aggregate.json':'a34a10ee1e29f224d668b3b0b64a0e7080902fa0',
}

def git_sha(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()

def load(name):
    if name not in BLOBS:raise ValueError('unregistered aggregate')
    raw=(HERE/name).read_bytes()
    if git_sha(raw)!=BLOBS[name]:raise ValueError('sealed R65 original aggregate drift')
    return json.loads(raw)

class PublicAggregateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if any(not (HERE/name).exists() for name in BLOBS):
            raise unittest.SkipTest('requires original GitHub public aggregate JSONs')

    def test_all_exact_git_blobs(self):
        for n in BLOBS:
            with self.subTest(n=n):self.assertIsInstance(load(n),dict)

    def test_four_conditions_and_stable_original_group_counts(self):
        x=load('r65_endogenous_aggregate.json')
        self.assertEqual(x['meta']['sessions'],24)
        self.assertEqual(x['meta']['groups'],48)
        self.assertEqual(sum(x['groupLevelInformedCountInEndogenous'].values()),48)
        for trt in ('No','Partial','Full','Endogenous'):
            for ep in ('early','late'):
                o=x['epochCounts'][trt][ep]
                self.assertEqual(o['oldA4'],o['allSixStay']+o['balancedSwap']+o['leaveA4'])

    def test_endogenous_vs_full_temporal_change(self):
        x=load('r65_endogenous_aggregate.json')
        full=x['lateMinusEarlyByTreatment']['Full']
        endo=x['lateMinusEarlyByTreatment']['Endogenous']
        self.assertAlmostEqual(full,150/257-34/154)
        self.assertAlmostEqual(endo,82/224-82/219)
        self.assertAlmostEqual(x['EndogenousMinusFullDifference'],endo-full)
        self.assertLess(x['pairedSessionBootstrap']['descriptive95'][1],0)
        self.assertIn('always last',x['warnings'][0])

    def test_two_model_and_two_seed_ssm_are_still_theories(self):
        x=load('r65_ssm_fitted_aggregate.json')
        for seed in ('seed_20261121','seed_20261123'):
            block=x[seed]
            self.assertEqual(block['repetitionsPerModel'],5000)
            for name in ('author_fitted_full_ssmq3','author_fitted_full_ssm1q4','author_R7_ssm5'):
                v=block['models'][name]
                self.assertLess(v['lateMinusEarly'],0)
                self.assertAlmostEqual(v['earlyP'],v['earlyA4StayCount']/v['earlyOldA4Count'])
                self.assertAlmostEqual(v['lateP'],v['lateA4StayCount']/v['lateOldA4Count'])
        self.assertFalse(x['meta']['authorRNGParity'])

    def test_age_binning_does_not_define_a_unique_explanation(self):
        x=load('r65_streak_aggregate.json')
        full=x['Full']
        for bins in ('fourBins','twoBins'):
            v=full[bins]
            self.assertAlmostEqual(v['composition']+v['withinAgeBin'],full['totalA4StayIncrease'])
        self.assertNotAlmostEqual(full['twoBins']['composition'],full['fourBins']['composition'])
        self.assertIn('NOT causal',x['scope'])

    def test_mutation_or_unregistered_read_rejected(self):
        with self.assertRaises(ValueError):load('participant_rows.csv')
        for n in BLOBS:
            with self.assertRaises(AssertionError):
                self.assertEqual(git_sha((HERE/n).read_bytes()+b' '),BLOBS[n])

    def test_public_json_contains_no_raw_person_records(self):
        forbidden=(b'"actor"',b'"subject"',b'"participant_id"',b'"participant_rows"',b'"individual_records"')
        for n in BLOBS:
            raw=(HERE/n).read_bytes()
            for marker in forbidden:self.assertNotIn(marker,raw)

if __name__=='__main__':unittest.main()
