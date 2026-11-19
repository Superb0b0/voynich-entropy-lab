"""Offline regression tests for the fail-closed attempt verifier."""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import call, patch

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

    def test_no_active_attempt_writes_explicit_not_verified_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "repo"
            attempt = root / "attempts" / "001-legacy"
            attempt.mkdir(parents=True)
            bundle_dir = pathlib.Path(temp) / "training"
            bundle_dir.mkdir()
            payload = b"training-only"
            (bundle_dir / "sample.txt").write_bytes(payload)
            bundle = {
                "schema": "voynich-training-only-bundle",
                "schema_version": 1,
                "policy_manifest_sha256": v.PINNED_POLICY_SHA256,
                "source_holdout_blob_sha1": "a" * 40,
                "source_corpus_sha256": {"sample.txt": "b" * 64},
                "training_corpus_sha256": {"sample.txt": hashlib.sha256(payload).hexdigest()},
                "filtered_page_block_counts": {"sample.txt": 1},
            }
            (bundle_dir / "training_manifest.json").write_text(json.dumps(bundle), encoding="utf-8")
            exceptions = root / "legacy.json"
            exceptions.write_text(json.dumps({
                "schema": "voynich-legacy-attempt-exceptions",
                "schema_version": 1,
                "exceptions": [{
                    "attempt_id": "001-legacy",
                    "status": "NOT_VERIFIABLE_LEGACY",
                    "recorded_on": "2026-11-19",
                    "reason": "Historical execution contract unavailable.",
                    "evidence": ["issue #23", "issue #27"],
                }],
            }), encoding="utf-8")
            with (
                patch.object(v, "ROOT", root),
                patch.object(v, "EXCEPTIONS", exceptions),
                patch.object(v, "shutil", create=True) as shutil_mock,
            ):
                shutil_mock.which.return_value = "/usr/bin/strace"
                with self.assertRaisesRegex(RuntimeError, "No active attempt was replayed"):
                    v.main(["--data-dir", str(bundle_dir)])
            summary = json.loads((root / "verification_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "NOT_VERIFIED_NO_ACTIVE_ATTEMPTS")
            self.assertEqual(summary["verified_attempts"], [])
            self.assertEqual(summary["not_verifiable_legacy"], ["001-legacy"])

    def test_verifier_does_not_read_holdout(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("HOLDOUT.read_text", source)
        self.assertNotIn("HOLDOUT.read_bytes", source)


class Archive008Tests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.archive = self.root / "attempts" / "008-depend-firstclass-reuse"
        self.archive.mkdir(parents=True)
        self.bundle_dir = self.root / "training"
        self.bundle_dir.mkdir()
        payload = b"3\n"
        (self.bundle_dir / "sample.txt").write_bytes(payload)
        (self.bundle_dir / "training_manifest.json").write_text(json.dumps({
            "schema": "voynich-training-only-bundle",
            "schema_version": 1,
            "policy_manifest_sha256": v.PINNED_POLICY_SHA256,
            "source_holdout_blob_sha1": "a" * 40,
            "source_corpus_sha256": {"sample.txt": "b" * 64},
            "training_corpus_sha256": {"sample.txt": hashlib.sha256(payload).hexdigest()},
            "filtered_page_block_counts": {"sample.txt": 1},
        }))
        self.summary_path = self.root / "verification_summary.json"
        self.exceptions = {}
        self.real_strace = shutil.which("strace")
        self.enterContext(patch.object(v, "ROOT", self.root))
        self.enterContext(patch.object(v.shutil, "which", return_value="/usr/bin/strace"))
        self.enterContext(patch.object(v, "load_legacy_exceptions", return_value=self.exceptions))
        self.forbidden = {self.root / "data" / "sample.txt"}

    def run_verifier(self):
        v.main(["--data-dir", str(self.bundle_dir)])

    def test_archive_and_legacy_do_not_satisfy_active_gate(self):
        legacy = self.root / "attempts" / "001-legacy"
        legacy.mkdir()
        self.exceptions[legacy.name] = {"status": "NOT_VERIFIABLE_LEGACY"}
        with patch.object(v, "verify_attempt") as replay:
            with self.assertRaisesRegex(RuntimeError, "No active attempt was replayed"):
                self.run_verifier()
        replay.assert_called_once_with(self.archive, self.bundle_dir, self.forbidden)
        summary = json.loads(self.summary_path.read_text())
        self.assertEqual(summary["status"], "NOT_VERIFIED_NO_ACTIVE_ATTEMPTS")
        self.assertEqual(summary["verified_attempts"], [])
        self.assertEqual(summary["not_verifiable_legacy"], [legacy.name])
        self.assertEqual(summary["technical_replays"], [{
            "attempt_id": self.archive.name,
            "replay_status": "REPRODUCED",
            "preregistration_status": "NOT_ATTESTABLE_FROM_ARCHIVE",
        }])

    def test_only_separate_active_attempt_counts(self):
        active = self.root / "attempts" / "099-synthetic-active"
        active.mkdir()
        with patch.object(v, "verify_attempt") as replay:
            self.run_verifier()
        self.assertEqual(replay.call_args_list, [
            call(self.archive, self.bundle_dir, self.forbidden),
            call(active, self.bundle_dir, self.forbidden),
        ])
        summary = json.loads(self.summary_path.read_text())
        self.assertEqual(summary["status"], "VERIFIED")
        self.assertEqual(summary["verified_attempts"], [active.name])
        self.assertEqual(summary["not_verifiable_legacy"], [])
        self.assertEqual([item["attempt_id"] for item in summary["technical_replays"]], [self.archive.name])

    def test_failed_archive_replay_cannot_leave_a_previous_success(self):
        self.summary_path.write_text('{"status":"VERIFIED"}')
        with patch.object(v, "verify_attempt", side_effect=RuntimeError("numeric mismatch")):
            with self.assertRaisesRegex(RuntimeError, "numeric mismatch"):
                self.run_verifier()
        self.assertFalse(self.summary_path.exists())

    def test_archive_still_requires_execution_contract(self):
        with self.assertRaisesRegex(RuntimeError, "missing attempt.yml"):
            self.run_verifier()
        self.assertFalse(self.summary_path.exists())

    def test_traced_toy_replay_matches_then_rejects_divergence(self):
        if not self.real_strace or subprocess.run(
            [self.real_strace, "-o", os.devnull, "--", "true"], capture_output=True
        ).returncode:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("The GitHub runner must be able to run strace for the synthetic replay")
            self.skipTest("strace needs a Linux host with permitted ptrace")
        (self.archive / "attempt.yml").write_text(json.dumps({
            "seed": 7, "tolerance": 0.000001, "command": [sys.executable, "toy.py"],
        }))
        (self.archive / "toy.py").write_text(
            "import json, os\n"
            "from pathlib import Path\n"
            "value = int((Path(os.environ['VOYNICH_DATA_DIR']) / 'sample.txt').read_text())\n"
            "Path('results_ci.json').write_text(json.dumps({'n': value}))\n"
        )
        expected = self.archive / "results.json"
        expected.write_text('{"n":3.0000005}')
        with self.assertRaisesRegex(RuntimeError, "No active attempt was replayed"):
            self.run_verifier()
        summary = json.loads(self.summary_path.read_text())
        self.assertEqual(summary["status"], "NOT_VERIFIED_NO_ACTIVE_ATTEMPTS")
        self.assertEqual(summary["technical_replays"][0]["replay_status"], "REPRODUCED")
        expected.write_text('{"n":8}')
        with self.assertRaisesRegex(RuntimeError, "tolerance="):
            self.run_verifier()
        self.assertFalse(self.summary_path.exists())

    def test_archive_cannot_be_listed_as_legacy(self):
        self.exceptions[self.archive.name] = {"status": "NOT_VERIFIABLE_LEGACY"}
        with self.assertRaisesRegex(RuntimeError, "cannot be a legacy exception"):
            self.run_verifier()

    def test_renamed_archive_cannot_be_counted_as_active(self):
        self.archive.rename(self.archive.with_name("008-renamed"))
        with self.assertRaisesRegex(RuntimeError, "reserved attempt 008"):
            self.run_verifier()


if __name__ == "__main__":
    unittest.main()
