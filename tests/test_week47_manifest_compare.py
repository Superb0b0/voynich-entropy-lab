"""Synthetic-only regression tests for the W47 manifest comparator."""
import importlib.util
import pathlib
import tempfile
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "research/week47-qo-decision/compare_structural_manifests.py"
spec = importlib.util.spec_from_file_location("w47_manifest_compare", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PARSER_PATH = pathlib.Path(__file__).resolve().parents[1] / \
    "experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py"
parser_spec = importlib.util.spec_from_file_location("w47_rc12_parser", PARSER_PATH)
rc12 = importlib.util.module_from_spec(parser_spec)
parser_spec.loader.exec_module(rc12)


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

    def test_dangling_block_reference_rejected_even_when_both_sides_match(self):
        a, b = fixture(), fixture()
        a["loci"][0]["block_id"] = "missing"
        b["loci"][0]["block_id"] = "missing"
        result = m.compare(a, b)
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "unknown_block_reference"
                            for d in result["differences"]))

    def test_block_page_mismatch_rejected_even_when_both_sides_match(self):
        a, b = fixture(), fixture()
        a["blocks"][0]["page"] = "other-page"
        b["blocks"][0]["page"] = "other-page"
        result = m.compare(a, b)
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "block_page_mismatch"
                            for d in result["differences"]))

    def test_dangling_next_locus_reference_rejected_even_when_both_sides_match(self):
        a, b = fixture(), fixture()
        a["loci"][0]["next_locus_id"] = "missing"
        b["loci"][0]["next_locus_id"] = "missing"
        result = m.compare(a, b)
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "unknown_locus_reference"
                            for d in result["differences"]))

    def test_next_locus_must_be_physical_neighbor_in_same_block(self):
        a, b = fixture(), fixture()
        a["loci"][0]["next_locus_id"] = "l2"
        b["loci"][0]["next_locus_id"] = "l2"
        a["loci"][1]["physical_index"] = 4
        b["loci"][1]["physical_index"] = 4
        result = m.compare(a, b)
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "invalid_adjacency_reference"
                            for d in result["differences"]))

    def test_non_object_manifest_fails_closed_without_exception(self):
        result = m.compare([], {})
        self.assertEqual(result["status"], "DIFFERENCES")
        self.assertTrue(any(d["error"] == "invalid_top_level_object"
                            for d in result["differences"]))

    def test_rc12_synthetic_locus_mapping_and_token_cleaning(self):
        source = ("<f1r> <! $L=A>\n"
                  "<f1r.1,*P0> <%>alpha{beta}<$>\n"
                  "<f1r.2,*P0> zha[xyz]o\n"
                  "<fRos.1,*P0> <~>go\n")
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "synthetic.ivtff"
            path.write_text(source, encoding="utf-8")
            result = rc12.parse_corpus(path, verify_source=False)
        rows = result["records"]
        self.assertEqual(
            [(r["physical_line"], r["locus_id"], r["folio"], r["line_index"], r["tokens"])
             for r in rows],
            [(2, "f1r.1", "f1r", 1, ["alphabeta"]),
             (3, "f1r.2", "f1r", 2, ["zha", "o"]),
             (4, "fRos.1", "fRos", 1, ["go"])])
        self.assertEqual(result["counts"]["canonical_loci"], 3)
        self.assertEqual(result["counts"]["token_count"], 4)

    def test_rc12_synthetic_mapping_rejects_malformed_locus_id(self):
        source = "<f1r.1a,*P0> word\n"
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "synthetic.ivtff"
            path.write_text(source, encoding="utf-8")
            with self.assertRaisesRegex(rc12.ParseFailure, "malformed locus identifier"):
                rc12.parse_corpus(path, verify_source=False)


if __name__ == "__main__":
    unittest.main()
