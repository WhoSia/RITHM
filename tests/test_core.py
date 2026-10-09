import csv
import pathlib
import tempfile
import unittest
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rithm20 import welfare,nash_side_counts,analyze,pay_main,pay_side
FIX=ROOT/"tests/fixtures/study1-mini.csv"
class HumanGroupTests(unittest.TestCase):
 def test_game(self):
  self.assertEqual(welfare(7),181)
  self.assertEqual(welfare(6),180)
  self.assertEqual(nash_side_counts(),[6])
  self.assertEqual(pay_main(6)-pay_side(7),3)
 def test_micro_to_macro(self):
  x=analyze(FIX)
  self.assertEqual(x["individual_decisions"],36)
  self.assertEqual(x["group_round_count"],2)
  self.assertEqual(x["mean_group_welfare"],180.5)
  self.assertEqual(x["mean_dispersion_component"],1.25)
  self.assertEqual(x["group_transitions"],1)
  self.assertEqual(x["mean_gross_switches"],1)
  self.assertEqual(x["welfare_decline_transitions"],1)
 def test_strict_source_guard(self):
  with self.assertRaisesRegex(ValueError,"Original source universe"):
   analyze(FIX,strict=True)
 def test_duplicate_refused(self):
  raw=FIX.read_text()
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/"dup.csv"
   p.write_text(raw+raw.splitlines()[1]+"\n")
   with self.assertRaisesRegex(ValueError,"Duplicate"):
    analyze(p)
 def test_profit_refused(self):
  with FIX.open(newline="") as f:
   data=list(csv.DictReader(f))
  data[0]["Profit"]="999"
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/"bad.csv"
   with p.open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
   with self.assertRaisesRegex(ValueError,"payoff mismatch"):
    analyze(p)
if __name__=="__main__":unittest.main()
