"""Disposable synthetic tests for treatment onset and history selection."""
import csv
import tempfile
import unittest
from pathlib import Path

from rithm20_information import describe, selection_check

COLUMNS = ["Period","Subject","Profit","LaneM","LaneS","S","M",
           "Session","Treatment","switch","infotreat"]


def fixture(path, bad_info=False):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for session in range(1, 5):
            for period in (49, 50, 51):
                for subject in range(1, 19):
                    is_side = subject <= 6
                    info = (period > 50 and
                            (session == 2 or (session in (3,4) and subject <= 4)))
                    if bad_info and session == 2 and period == 51 and subject == 18:
                        info = False
                    writer.writerow({
                        "Period": period, "Subject": subject,
                        "Profit": 10, "LaneM": int(not is_side),
                        "LaneS": int(is_side), "S": 6, "M": 12,
                        "Session": session, "Treatment": session,
                        "switch": "" if period == 49 else 0,
                        "infotreat": int(info)
                    })


class InformationDesignTests(unittest.TestCase):
    def test_clean_four_arm_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"study1-mini-information.csv"
            fixture(p)
            result = describe(p)
            self.assertEqual(result["group_rounds"], 12)
            self.assertEqual(result["independent_session_units"], 4)
            self.assertEqual(len(result["treatment_summaries"]), 4)
            self.assertTrue(all(x["delta_welfare"] == 0
                                for x in result["sessions"]))
            self.assertEqual([s["n_informed"] for s in result["sessions"]],
                             [0,18,4,4])

    def test_information_dose_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"bad-study1.csv"
            fixture(p, bad_info=True)
            with self.assertRaisesRegex(ValueError, "Information onset or dose"):
                describe(p)

    def test_frequent_selection_is_not_arbitrary(self):
        counts = {1: 0, 2: 2, 3: 8, 4: 10}
        selection_check(3, counts, {3,4})
        with self.assertRaisesRegex(ValueError, "Frequent-4"):
            selection_check(3, counts, {1,2})

    def test_infrequent_selection_is_not_arbitrary(self):
        counts = {1: 0, 2: 2, 3: 8, 4: 10}
        selection_check(4, counts, {1,2})
        with self.assertRaisesRegex(ValueError, "Infrequent-4"):
            selection_check(4, counts, {3,4})

    def test_original_strict_contract_not_faked_by_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"study1-mini-information.csv"
            fixture(p)
            with self.assertRaisesRegex(ValueError, "Original source universe"):
                describe(p, strict=True)


if __name__ == "__main__":
    unittest.main()
