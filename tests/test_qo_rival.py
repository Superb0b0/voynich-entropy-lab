"""Regression tests: recto/verso boundaries, heldout leaves, leaf shuffle and adjacency."""
import importlib.util
import random
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "qo_rival_calibration.py"
spec = importlib.util.spec_from_file_location("qo_rival_calibration", SCRIPT)
qo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qo)


class FakeSource:
    def __init__(self, raw):
        self.raw = raw
    def read_bytes(self):
        return self.raw


class QoRivalRegression(unittest.TestCase):
    def parse_synthetic(self, text):
        raw = text.encode("utf-8")
        import hashlib
        with patch.object(qo, "SOURCE", FakeSource(raw)), patch.object(qo, "SHA", hashlib.sha256(raw).hexdigest()):
            return qo.parse()

    def test_recto_verso_do_not_merge(self):
        data = ("<f1r> <! page\n"
                "<f1r.1,@P0> qokedy other\n"
                "<f1r.2,+P0> qokedy other\n"
                "<f1v> <! page\n"
                "<f1v.1,@P0> qokedy other\n"
                "<f1v.2,+P0> qokedy other\n")
        groups = self.parse_synthetic(data)
        self.assertEqual(set(groups), {("f1r", 1), ("f1v", 1)})
        self.assertEqual(qo.count(groups), (2, 2))

    def test_holdout_excludes_both_sides(self):
        data = ("<f2r> <! page\n"
                "<f2r.1,@P0> qokedy other\n"
                "<f2r.2,+P0> qokedy other\n"
                "<f2v> <! page\n"
                "<f2v.1,@P0> qokedy other\n"
                "<f2v.2,+P0> qokedy other\n"
                "<f1r> <! page\n"
                "<f1r.1,@P0> qokedy other\n"
                "<f1r.2,+P0> other qokedy\n")
        groups = self.parse_synthetic(data)
        self.assertEqual(set(groups), {("f1r", 1)})
        self.assertEqual(qo.count(groups), (0, 1))

    def test_nonconsecutive_lines_not_counted(self):
        groups = {("f1r", 1): [(1, "qokedy"), (3, "qokedy")]}
        self.assertEqual(qo.count(groups), (0, 0))

    def test_within_leaf_permutation_preserves_page_lengths(self):
        groups = {("f1r", 1): [(1, "qokedy"), (2, "daiin")],
                  ("f1v", 1): [(1, "ol"), (2, "chedy")],
                  ("f3r", 1): [(1, "qokai"), (2, "otedy")]}
        out = qo.permute(groups, "within_folio", random.Random(4))
        self.assertEqual({k: len(v) for k, v in out.items()}, {k: len(v) for k, v in groups.items()})
        self.assertCountEqual([w for k,v in out.items() if k[0].startswith("f1") for _,w in v],
                              ["qokedy", "daiin", "ol", "chedy"])
        self.assertCountEqual([w for _,w in out[("f3r", 1)]], ["qokai", "otedy"])


if __name__ == "__main__":
    unittest.main()
