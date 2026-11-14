import pathlib
import tempfile
import unittest
from scripts.inventory_attempts import inventory

def item(state):
    return {"state": state, "reason": "archived, not replayed", "evidence": "TESTS.md",
            "classified_on": "2026-11-14", "decision_commit": "39de351",
            "decision_owner": "maintainer pending confirmation", "eligible_for_evidence_promotion": False}

class InventoryTests(unittest.TestCase):
    def check(self, state, registered=True, config=False):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            folder = root / "001-example"
            folder.mkdir()
            if config:
                (folder / "attempt.yml").write_text("seed: 42\n")
            registry = {"attempts": {"001-example": item(state)} if registered else {}}
            return inventory(root, registry)
    def test_known_quarantine_missing_config_is_not_evidence(self):
        rows, errors = self.check("quarantined")
        self.assertFalse(errors)
        self.assertFalse(rows[0]["evidence_eligible"])
        self.assertEqual(rows[0]["outcome"], "QUARANTINED")
    def test_unknown_fails(self):
        _, errors = self.check("quarantined", registered=False)
        self.assertTrue(any("unknown" in e for e in errors))
    def test_unresolved_legacy_fails(self):
        _, errors = self.check("legacy")
        self.assertTrue(any("pending" in e for e in errors))
    def test_active_missing_config_fails(self):
        _, errors = self.check("active")
        self.assertTrue(any("missing attempt.yml" in e for e in errors))
    def test_active_with_config_is_inventory_eligible_only(self):
        rows, errors = self.check("active", config=True)
        self.assertFalse(errors)
        self.assertTrue(rows[0]["evidence_eligible"])

if __name__ == "__main__":
    unittest.main()
