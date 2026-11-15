"""G0 regression: malformed numeric and fRos loci must fail closed. Synthetic only."""
import hashlib
import unittest
from tools.g0_count_audit import analyze

CASES = {
    "valid_numeric": ("<f1r.1,@P0> qo", False),
    "valid_ros": ("<fRos.1,@P0> qo", False),
    "bad_numeric_no_close": ("<f1r.1,@P0 qo", True),
    "bad_ros_no_close": ("<fRos.1,@P0 qo", True),
    "bad_ros_line": ("<fRos.x,@P0> qo", True),
    "bad_ros_missing_comma": ("<fRos.1@P0> qo", True),
    "bad_ros_empty_line": ("<fRos.,@P0> qo", True),
    "unrelated_header": ("<metadata> sample", False),
}

class G0HeaderTest(unittest.TestCase):
    def test_synthetic_headers(self):
        for name, (line, expected_malformed) in CASES.items():
            with self.subTest(name=name):
                raw = (line + "\n").encode()
                rows, malformed = analyze(raw, "SYNTHETIC", hashlib.sha256(raw).hexdigest())
                self.assertEqual(bool(malformed), expected_malformed)
                if name.startswith("valid_"):
                    self.assertEqual(next(r for r in rows if r["locus_rule"] == "family_P")["loci"], 1)

if __name__ == "__main__":
    unittest.main()
