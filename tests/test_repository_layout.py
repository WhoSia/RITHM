"""Root-layout regression and verbatim preservation of original historical README."""
import hashlib
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
OLD_ROOT_README_GIT_BLOB="032b27bfd10716333b597f4010c57e5a91f0f4e0"
LEGACY_NAMES={
    "rithm20.py","rithm20_information.py","rithm22_audit.py",
    "rithm22_group_checks.py","rithm23_cost_contract.py",
    "rithm23_information_timing.py","rithm23_source_decode.py",
    "rithm23_welfare_bridge.py","rithm24_identification.py",
}

class RootSourceLayoutContract(unittest.TestCase):
    def test_nine_legacy_modules_reside_only_under_src(self):
        for name in LEGACY_NAMES:
            self.assertFalse((ROOT/name).exists(),name)
            self.assertTrue((ROOT/"src"/"rithm"/"legacy"/name).is_file(),name)

    def test_repro_is_maintained_once(self):
        self.assertFalse((ROOT/"README_REPRO.md").exists())
        self.assertTrue((ROOT/"docs"/"REPRODUCIBILITY.md").is_file())

    def test_exact_previous_readme_blob_preserved(self):
        # Git blob framing: sha1("blob "+length+NUL+exact bytes).
        raw=(ROOT/"docs"/"PROJECT_HISTORY_20261012.md").read_bytes()
        obj=b"blob "+str(len(raw)).encode()+bytes([0])+raw
        self.assertEqual(hashlib.sha1(obj).hexdigest(),
                         OLD_ROOT_README_GIT_BLOB)

if __name__=="__main__":
    unittest.main()
