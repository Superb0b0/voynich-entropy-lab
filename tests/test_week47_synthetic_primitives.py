"""Regression tests for synthetic-only W47 primitives.

No manuscript data, no HOLDOUT access, no scientific experiment.
"""
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "research/week47-qo-decision/synthetic_primitives.py"
spec = importlib.util.spec_from_file_location("w47_synthetic_primitives", PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def line(page, block, index, word):
    return dict(page=page, block=block, locus_index=index,
                first_word=word, folio="synthetic_folio")


class SyntheticW47Tests(unittest.TestCase):
    def test_only_immediate_physical_neighbors(self):
        rows = [line("p", "b", 1, "aa"), line("p", "b", 2, "aa"),
                line("p", "b", 4, "aa"), line("p", "c", 5, "aa"),
                line("q", "c", 6, "aa")]
        self.assertEqual(len(list(m.eligible_pairs(rows))), 1)
        self.assertEqual(m.repeat_count(rows), 1)

    def test_identical_words_permutation_invariant(self):
        rows = [line("p", "b", i, "aa") for i in range(1, 5)]
        self.assertEqual(m.repeat_count(rows), 3)
        self.assertEqual(m.permutation_counts(rows, replicates=30), [3] * 30)

    def test_distinct_words_never_repeat_with_two_rows(self):
        rows = [line("p", "b", 1, "aa"), line("p", "b", 2, "bb")]
        self.assertEqual(m.repeat_count(rows), 0)
        self.assertEqual(m.permutation_counts(rows, replicates=30), [0] * 30)

    def test_seed_replay(self):
        rows = [line("p", "b", i, word) for i, word in
                enumerate(["aa", "bb", "aa", "cc", "bb", "aa"], 1)]
        a = m.permutation_counts(rows, replicates=40, seed=20261116)
        b = m.permutation_counts(rows, replicates=40, seed=20261116)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 40)

    def test_empty_token_and_page_reset(self):
        rows = [line("p", "b", 1, "aa"), line("p", "b", 2, ""),
                line("p", "b", 3, "aa"), line("q", "b", 4, "aa")]
        self.assertEqual(list(m.eligible_pairs(rows)), [])
        self.assertEqual(m.repeat_count(rows), 0)

    def test_reject_duplicate_physical_locus(self):
        rows = [line("p", "b", 1, "aa"), line("p", "b", 1, "bb")]
        with self.assertRaisesRegex(ValueError, "physical locus"):
            m.repeat_count(rows)

    def test_reject_out_of_order_physical_locus(self):
        rows = [line("p", "b", 2, "aa"), line("p", "b", 1, "bb")]
        with self.assertRaisesRegex(ValueError, "physical locus"):
            m.permutation_counts(rows, replicates=2)

    def test_reject_invalid_locus_index(self):
        with self.assertRaises(ValueError):
            m.repeat_count([line("p", "b", True, "aa")])

    def test_invalid_replicates(self):
        with self.assertRaises(ValueError):
            m.permutation_counts([line("p", "b", 1, "aa")], replicates=0)


if __name__ == "__main__":
    unittest.main()
