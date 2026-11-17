"""Synthetic tests for HMAC-based training-page filtering; no corpus or holdout access."""
import hashlib
import hmac
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "tools" / "prepare_training_data.py"
spec = importlib.util.spec_from_file_location("prepare_training_data", SCRIPT)
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


class PrepareTrainingDataTests(unittest.TestCase):
    def test_hmac_filter_removes_complete_page(self):
        key = b"synthetic-test-key-with-32-bytes-min"
        protected = hmac.new(key, b"f2r", hashlib.sha256).hexdigest()
        text = (
            "<f1r> <! page\n<f1r.1,@P0> keep-one\n"
            "<f2r> <! page\n<f2r.1,@P0> remove-this-page\n"
            "<f3r> <! page\n<f3r.1,@P0> keep-three\n"
        )
        result, count = prep.sanitize_text(text, {protected}, key)
        self.assertEqual(count, 1)
        self.assertNotIn("<f2r>", result)
        self.assertNotIn("remove-this-page", result)
        self.assertIn("keep-one", result)
        self.assertIn("keep-three", result)

    def test_wrong_key_fails_closed(self):
        key = b"synthetic-test-key-with-32-bytes-min"
        wrong = hmac.new(b"another-synthetic-key-with-32-byte", b"f2r", hashlib.sha256).hexdigest()
        text = "<f2r> <! page\n<f2r.1,@P0> protected\n"
        with self.assertRaisesRegex(RuntimeError, "No protected pages matched"):
            prep.sanitize_text(text, {wrong}, key)

    def test_manifest_hash_pin_is_checked(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "manifest.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SHA-256 differs"):
                prep.load_policy_manifest(b"x" * 32, manifest_path=path, expected_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
