import unittest,tempfile
from pathlib import Path
from r66_t7_empirical_contract import check_authorized_source,pooled_joint_tail

class TestEmpiricalContract(unittest.TestCase):
    def test_synthetic_counts_no_ids(self):
        rows=[{'treatment':'Full','epoch':'late','prior_a':4,'a_to_b':3},
              {'treatment':'Full','epoch':'late','prior_a':4,'a_to_b':0},
              {'treatment':'No','epoch':'early','prior_a':5,'a_to_b':3}]
        r=pooled_joint_tail(rows)
        self.assertEqual(r['Full_late'],{'opportunities':2,'tail':1})
        self.assertEqual(r['No_early'],{'opportunities':0,'tail':0})
        self.assertNotIn('participant',str(r).lower())
    def test_source_hash_gate_blocks_other_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wrong.zip';p.write_bytes(b'not the approved source')
            with self.assertRaises(PermissionError):check_authorized_source(p)
    def test_reject_actor_identifier(self):
        with self.assertRaises(ValueError):
            pooled_joint_tail([{'treatment':'Full','epoch':'late','prior_a':4,'a_to_b':0,'actor_id':'x'}])
    def test_invalid_cutoff(self):
        with self.assertRaises(ValueError):pooled_joint_tail([],cutoff=2)
