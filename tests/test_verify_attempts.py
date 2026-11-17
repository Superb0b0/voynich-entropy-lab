"""Offline regression tests for the fail-closed attempt verifier."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "tools" / "verify_attempts.py"
spec = importlib.util.spec_from_file_location("verify_attempts", SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerifyTests(unittest.TestCase):
    def test_numeric_tolerance(self):
        v.compare({"x": [1.0, 2.0], "ok": True}, {"x": [1.001, 2.0], "ok": True}, 0.002)
        with self.assertRaises(RuntimeError):
            v.compare({"x": 1.0}, {"x": 1.1}, 0.002)

    def test_missing_and_extra_fields_fail(self):
        with self.assertRaises(RuntimeError):
            v.compare({"x": 1}, {"x": 1, "y": 2}, 0)

    def test_boolean_not_numeric(self):
        with self.assertRaises(RuntimeError):
            v.compare({"x": True}, {"x": 1}, 0)

    def test_training_bundle_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            safe = b"training-only"
            (root / "sample.txt").write_bytes(safe)
            bundle = {
                "schema": "voynich-training-only-bundle",
                "schema_version": 1,
                "policy_manifest_sha256": v.PINNED_POLICY_SHA256,
                "source_holdout_blob_sha1": "a" * 40,
                "source_corpus_sha256": {"sample.txt": "b" * 64},
                "training_corpus_sha256": {"sample.txt": hashlib.sha256(safe).hexdigest()},
                "filtered_page_block_counts": {"sample.txt": 1},
            }
            (root / "training_manifest.json").write_text(json.dumps(bundle), encoding="utf-8")
            validated = v.validate_training_bundle(root)
            self.assertEqual(validated["schema_version"], 1)
            (root / "sample.txt").write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "training bundle SHA-256 mismatch"):
                v.validate_training_bundle(root)

    def test_legacy_exception_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "exceptions.json"
            path.write_text(json.dumps({
                "schema": "voynich-legacy-attempt-exceptions",
                "schema_version": 1,
                "exceptions": [{
                    "attempt_id": "001-paragraph-header-key",
                    "status": "NOT_VERIFIABLE_LEGACY",
                    "recorded_on": "2026-11-17",
                    "reason": "Missing contemporaneous execution contract.",
                    "evidence": ["issue #23", "issue #27"],
                }],
            }), encoding="utf-8")
            with patch.object(v, "EXCEPTIONS", path):
                result = v.load_legacy_exceptions()
            self.assertEqual(result["001-paragraph-header-key"]["status"], "NOT_VERIFIABLE_LEGACY")

    def test_verifier_does_not_read_holdout(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("HOLDOUT.read_text", source)
        self.assertNotIn("HOLDOUT.read_bytes", source)


if __name__ == "__main__":
    unittest.main()
