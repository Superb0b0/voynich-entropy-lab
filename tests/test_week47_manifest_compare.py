"""Synthetic-only regression tests for the W47 manifest comparator."""
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "research/week47-qo-decision/compare_structural_manifests.py"
spec = importlib.util.spec_from_file_location("w47_manifest_compare", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    return {"blocks": [{"id": "b1", "page": "p1", "start": 1, "end": 2, "order": 1}],
            "loci": [{"id": "l1", "page": "p1", "block_id": "b1",
                      "physical_index": 1, "tokens": ["ab", "cd"],
                      "next_locus_id": "l2"},
                     {"id": "l2", "page": "p1", "block_id": "b1",
                      "physical_index": 2, "tokens": ["ef"],
                      "next_locus_id": None}]}


class ManifestCompareTests(unittest.TestCase):
    def test_identical(self):
        x = fixture()
        self.assertEqual(m.compare(x, fixture())["status"], "MATCH")

    def test_token_difference(self):
        a, b = fixture(), fixture()
        b["loci"][0]["tokens"] = ["ab", "xy"]
        r = m.compare(a, b)
        self.assertEqual(r["status"], "DIFFERENCES")
        self.assertTrue(any(d.get("field") == "tokens" for d in r["differences"]))

    def test_adjacency_difference(self):
        a, b = fixture(), fixture()
        b["loci"][0]["next_locus_id"] = None
        self.assertEqual(m.compare(a, b)["status"], "DIFFERENCES")

    def test_boundary_difference(self):
        a, b = fixture(), fixture()
        b["blocks"][0]["end"] = 3
        self.assertEqual(m.compare(a, b)["status"], "DIFFERENCES")

    def test_missing_id(self):
        a, b = fixture(), fixture()
        b["loci"].pop()
        self.assertTrue(any(d["error"] == "missing_id" for d in m.compare(a, b)["differences"]))

    def test_duplicate_id(self):
        a, b = fixture(), fixture()
        b["blocks"].append(dict(b["blocks"][0]))
        self.assertTrue(any(d["error"] == "duplicate_id" for d in m.compare(a, b)["differences"]))

    def test_both_missing_same_required_field_rejected(self):
        a, b = fixture(), fixture()
        del a["loci"][0]["next_locus_id"]
        del b["loci"][0]["next_locus_id"]
        result = m.compare(a, b)
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "missing_required_field" for d in result["differences"]))

    def test_both_invalid_token_types_rejected(self):
        a, b = fixture(), fixture()
        a["loci"][0]["tokens"] = "ab cd"
        b["loci"][0]["tokens"] = "ab cd"
        self.assertEqual(m.compare(a, b)["status"], "DIFFERENCES")

    def test_both_invalid_indices_rejected(self):
        a, b = fixture(), fixture()
        a["loci"][0]["physical_index"] = True
        b["loci"][0]["physical_index"] = True
        self.assertEqual(m.compare(a, b)["status"], "DIFFERENCES")

    def test_missing_required_field(self):
        a, b = fixture(), fixture()
        del b["loci"][0]["physical_index"]
        self.assertEqual(m.compare(a, b)["status"], "DIFFERENCES")


if __name__ == "__main__":
    unittest.main()
