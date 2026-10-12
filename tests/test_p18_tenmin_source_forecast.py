import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"/"p18_tenmin_source_forecast.py"
spec=importlib.util.spec_from_file_location("p18_clock",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TenMinutePhase(unittest.TestCase):
    def test_integer_invariance_exhaustive(self):
        for total in range(26):
            for even in range(total+1):
                odd=total-even
                for new_even in range(total+1):
                    self.assertEqual(total,mod.invariant_sum(
                        even,odd,new_even-even))
    def test_alias_sensitive_last_five(self):
        self.assertEqual(872,mod.invariant_sum(315,557,121))
        self.assertNotEqual(2*557,2*(557-121))
    def test_duplicate_invalid(self):
        rows=[(0,d,k,100.0,70.0)
             for d in range(1,29) for k in range(288)]
        rows.append((0,28,287,100.0,70.0))
        with self.assertRaisesRegex(ValueError,"duplicate"):
            mod.score_month(3,rows)
    def test_missing_pair_not_imputed(self):
        rows=[(0,d,k,100.0,70.0)
             for d in range(1,29) for k in range(288)
             if not (d==25 and k==2)]
        self.assertEqual(mod.score_month(3,rows)["complete_10min_pairs"],28*144-1)

if __name__=="__main__":
    unittest.main()
