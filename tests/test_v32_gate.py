"""Synthetic V3.2 gate regression tests. No Voynich inputs or protected folios."""
import hashlib
import json
import pathlib
import tempfile
import unittest
from scripts.validate_experiment import validate

class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        (self.root / "input.txt").write_bytes(b"synthetic only")
        self.protocol = {
            "experiment_id": "V32-TEST-SYNTH",
            "hypothesis": "synthetic control",
            "falsifiable_prediction": "synthetic result exceeds 0.5",
            "primary_metric": "synthetic_metric",
            "decision_threshold": 0.5,
            "null_model": "synthetic permutation",
            "data_version": "synthetic-v1",
            "discovery_folia": ["synthetic_A"],
            "test_folia": ["synthetic_B"],
            "inputs": [{"path": "input.txt",
                        "sha256": hashlib.sha256(b"synthetic only").hexdigest()}]
        }
        self.write_protocol()
    def write_protocol(self):
        (self.root / "protocol.json").write_text(json.dumps(self.protocol))
    def errors(self):
        return validate(self.root)
    def test_valid(self):
        self.assertFalse(any(self.errors().values()))
    def test_incomplete_protocol_rejected(self):
        del self.protocol["null_model"]
        self.write_protocol()
        self.assertTrue(self.errors()["protocol"])
    def test_overlap_rejected(self):
        self.protocol["test_folia"] = ["synthetic_A"]
        self.write_protocol()
        self.assertTrue(self.errors()["data_split"])
    def test_hash_tamper_rejected(self):
        (self.root / "input.txt").write_bytes(b"tampered")
        self.assertTrue(self.errors()["integrity"])
    def test_post_result_promotion_rejected(self):
        digest = hashlib.sha256((self.root / "protocol.json").read_bytes()).hexdigest()
        (self.root / "results.json").write_text(json.dumps({
            "status": "VALIDATED", "protocol_sha256": digest,
            "deviations": [{"timestamp": "2026-11-15T00:00:00Z",
                            "reason": "changed after outcome", "after_results": True}]
        }))
        self.assertTrue(self.errors()["promotion"])
    def test_result_protocol_mismatch_rejected(self):
        (self.root / "results.json").write_text(json.dumps({
            "status": "EXPLORATORY", "protocol_sha256": "0"*64, "deviations": []
        }))
        self.assertTrue(self.errors()["promotion"])
    def test_exploratory_bound_result_allowed(self):
        digest = hashlib.sha256((self.root / "protocol.json").read_bytes()).hexdigest()
        (self.root / "results.json").write_text(json.dumps({
            "status": "EXPLORATORY", "protocol_sha256": digest, "deviations": []
        }))
        self.assertFalse(any(self.errors().values()))

if __name__ == "__main__":
    unittest.main()
