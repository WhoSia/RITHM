"""Privacy, synthetic source rejection and result-form contract for R57."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from r57_results import generate, PRIMARY_SHRINK, SENSITIVITY_SHRINKS
from r57_history_cv import MODELS

class ResultsContract(unittest.TestCase):
    def test_source_requires_exact_original_sha_before_reading(self):
        with TemporaryDirectory() as d:
            p=Path(d)/'fake.zip'
            p.write_bytes(b'not real data')
            with self.assertRaisesRegex(ValueError,'authorized source SHA256'):
                generate(p)

    def test_fixed_models_and_smoothing_are_not_tuned_on_heldout(self):
        self.assertEqual(PRIMARY_SHRINK,20)
        self.assertEqual(SENSITIVITY_SHRINKS,(5,80))
        self.assertEqual(set(MODELS),{
            'state_independent','tenure','received_profit','tenure_profit',
            'informed','tenure_profit_informed'})

if __name__=='__main__':unittest.main()
