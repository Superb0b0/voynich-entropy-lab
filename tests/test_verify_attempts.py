"""Offline regression tests for the fail-closed attempt verifier."""
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SCRIPT=pathlib.Path(__file__).resolve().parents[1]/"tools"/"verify_attempts.py"
spec=importlib.util.spec_from_file_location("verify_attempts",SCRIPT)
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

class VerifyTests(unittest.TestCase):
    def test_numeric_tolerance(self):
        v.compare({"x":[1.0,2.0],"ok":True},{"x":[1.001,2.0],"ok":True},0.002)
        with self.assertRaises(RuntimeError):
            v.compare({"x":1.0},{"x":1.1},0.002)
    def test_missing_and_extra_fields_fail(self):
        with self.assertRaises(RuntimeError):
            v.compare({"x":1},{"x":1,"y":2},0)
    def test_boolean_not_numeric(self):
        with self.assertRaises(RuntimeError):
            v.compare({"x":True},{"x":1},0)
    def test_sanitize_removes_entire_protected_page(self):
        raw="<f1r> <! page\n<f1r.1,@P0> safe\n<f2r> <! page\n<f2r.1,@P0> secret\n<f3r> <! page\n<f3r.1,@P0> safeagain\n"
        result=v.sanitize(raw,{"f2r"})
        self.assertNotIn("secret",result)
        self.assertNotIn("<f2r>",result)
        self.assertIn("safeagain",result)
    def test_manifest_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/"data").mkdir()
            (root/"data"/"sample.txt").write_bytes(b"abc")
            (root/"MANIFEST.md").write_text("| File | Bytes | SHA-256 |\n|---|---|---|\n| `data/sample.txt` | 3 | `"+("0"*64)+"` |\n")
            with patch.object(v,"ROOT",root),patch.object(v,"MANIFEST",root/"MANIFEST.md"):
                with self.assertRaisesRegex(RuntimeError,"SHA256 mismatch"):
                    v.hashes()

if __name__=="__main__":
    unittest.main()
