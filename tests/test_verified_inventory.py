import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from verified_inventory import attest

class InventoryTests(unittest.TestCase):
    def setup_case(self, td, content):
        root = pathlib.Path(td)
        (root / "safe").mkdir()
        (root / "safe" / "a.txt").write_text(content)
        return root

    def test_positive(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f3v> <!\n")
            n = attest(root / "safe", {"f2r"}, ["a.txt"], root / "out.json")
            self.assertEqual(n, 2)
            self.assertEqual(json.loads((root / "out.json").read_text())["eligible_page_ids"], ["f1r", "f3v"])

    def test_protected_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f2r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "protected content"):
                attest(root / "safe", {"f2r"}, ["a.txt"], root / "out.json")
            self.assertFalse((root / "out.json").exists())

    def test_empty_policy_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "policy empty"):
                attest(root / "safe", set(), ["a.txt"], root / "out.json")

    def test_unexpected_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n")
            (root / "safe" / "extra.txt").write_text("<f1r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "set mismatch"):
                attest(root / "safe", {"f2r"}, ["a.txt"], root / "out.json")

    def test_two_transcriptions_equal_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f3v> <!\n")
            (root / "safe" / "b.txt").write_text("<f3v> <!\n<f1r> <!\n")
            self.assertEqual(attest(root / "safe", {"f2r"}, ["a.txt", "b.txt"], root / "out.json"), 2)

    def test_two_transcriptions_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f3v> <!\n")
            (root / "safe" / "b.txt").write_text("<f1r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                attest(root / "safe", {"f2r"}, ["a.txt", "b.txt"], root / "out.json")
            self.assertFalse((root / "out.json").exists())

    def test_explicit_single_unmatched_quarantine(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f3v> <!\n")
            (root / "safe" / "b.txt").write_text("<f1r> <!\n")
            self.assertEqual(attest(root / "safe", {"f2r"}, ["a.txt", "b.txt"], root / "out.json",
                                    quarantine_single_unmatched=True), 1)
            data=json.loads((root / "out.json").read_text())
            self.assertEqual(data["quarantine"]["count"], 1)
            self.assertEqual(data["eligible_page_ids"], ["f1r"])

    def test_explicit_quarantine_rejects_two_mismatches(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n<f3v> <!\n<f4r> <!\n")
            (root / "safe" / "b.txt").write_text("<f1r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                attest(root / "safe", {"f2r"}, ["a.txt", "b.txt"], root / "out.json",
                       quarantine_single_unmatched=True)

    def test_protected_in_second_transcription_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n")
            (root / "safe" / "b.txt").write_text("<f1r> <!\n<f2r> <!\n")
            with self.assertRaisesRegex(RuntimeError, "protected content"):
                attest(root / "safe", {"f2r"}, ["a.txt", "b.txt"], root / "out.json")
            self.assertFalse((root / "out.json").exists())

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.setup_case(td, "<f1r> <!\n")
            (root / "out.json").write_text("original")
            with self.assertRaisesRegex(RuntimeError, "overwrite"):
                attest(root / "safe", {"f2r"}, ["a.txt"], root / "out.json")
            self.assertEqual((root / "out.json").read_text(), "original")

if __name__ == "__main__":
    unittest.main()
