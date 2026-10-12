"""Run with: python -m unittest discover -s tests -p test_traffic_sources.py
No original source files are required for safe synthetic tests.
"""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1] / "tools" / "traffic_sources"
sys.path.insert(0,str(ROOT))
from split_csv_stream import split_csv, verify_parts
from audit_seoul_5min import audit

class TrafficSourcesTest(unittest.TestCase):
    def test_multiline_cp949_and_digest(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"example.csv"
            with source.open("w",encoding="cp949",newline="") as f:
                w=csv.writer(f)
                w.writerow(["날짜","구간","교통량"])
                w.writerow(["2025-01-01","신내IC,구리","12"])
                w.writerow(["2025-01-02","인용 \"단어\"\n다음 줄","0"])
                w.writerows([["2025-01-03","세종",str(i)] for i in range(800)])
            target=Path(d)/"parts"
            manifest=split_csv(source,target,max_mb=.006)
            self.assertGreater(manifest["part_count"],1)
            self.assertEqual(verify_parts(target),802)
            self.assertTrue(all(p["bytes"]<=6000 for p in manifest["parts_in_order"]))

    def test_reject_duplicate_source_clock(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.csv"
            with source.open("w",encoding="cp949",newline="") as f:
                w=csv.writer(f)
                w.writerow(["기간\t","노선 ID","노선명","구간 ID","구간명","구간 길이",
                             "5분 코드","교통량","속도","점유율"])
                row=["2022-08-01","A","북부간선","L","구리~신내","1813.4","0000","1","60","5"]
                w.writerow(row)
                w.writerow(row)
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                audit(source)

if __name__=="__main__":
    unittest.main()
