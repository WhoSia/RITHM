"""No-source regression of the three distinct author-paper/script populations."""
import unittest
from r27_audit_population_contracts import CONTRACTS,EXPECTED,included

class TestPopulationContracts(unittest.TestCase):
    def test_disputed_pilot_and_session101_have_distinct_contracts(self):
        for name,yes2,yes101 in [
            ("published_main_24",False,False),
            ("exclude_pilot2_include101_25",False,True),
            ("literal_author_R_filter_26",True,True),
        ]:
            self.assertEqual(included(2,3,20,name),yes2)
            self.assertEqual(included(101,3,20,name),yes101)
            self.assertFalse(included(1,3,20,name))
    def test_all_contracts_full_info_only_and_40_rounds(self):
        for name in CONTRACTS:
            for trt in (1,2,4):
                self.assertFalse(included(101,trt,20,name))
            for t in (0,41,-1):
                self.assertFalse(included(103,3,t,name))
            self.assertTrue(included(103,3,1,name))
            self.assertTrue(included(103,3,40,name))
    def test_counts_are_not_the_same_population(self):
        self.assertEqual(EXPECTED["published_main_24"],(24,48,1824))
        self.assertEqual(EXPECTED["exclude_pilot2_include101_25"],(25,51,1938))
        self.assertEqual(EXPECTED["literal_author_R_filter_26"],(26,53,2014))
    def test_unknown_contract_fails_closed(self):
        with self.assertRaises(ValueError):included(101,3,20,"author_approved")
        with self.assertRaises(ValueError):included("101",3,20,CONTRACTS[0])

if __name__=="__main__":unittest.main()
