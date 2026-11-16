#!/usr/bin/env python3
"""W47 synthetic-only adjacency checks. No Voynich corpus or real runner access.

This is an engineering fixture, NOT a parser parity attestation or experiment.
Rows are already canonicalized by an independently validated parser; never infer
adjacency from array position alone.
"""
from collections import defaultdict
import random
import unittest


def eligible_pairs(rows):
    """Return physical-adjacent pairs, without bridging gaps, pages or blocks.

    Required row keys: page, block, physical_line, word. A physical_line is an
    integer P-locus sequence index supplied by an audited parser, not a
    renumbering of eligible/nonempty rows.
    """
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        assert set(("page", "block", "physical_line", "word")) <= row.keys()
        assert isinstance(row["physical_line"], int)
        assert isinstance(row["word"], str) and row["word"]
        key = (row["page"], row["block"], row["physical_line"])
        if key in seen:
            raise ValueError("Duplicate physical locus")
        seen.add(key)
        groups[(row["page"], row["block"])].append(row)
    pairs = []
    for key, lines in groups.items():
        lines.sort(key=lambda r: r["physical_line"])
        for left, right in zip(lines, lines[1:]):
            if right["physical_line"] == left["physical_line"] + 1:
                pairs.append((left["word"], right["word"]))
    return pairs


def synthetic_permutation_counts(rows, repeats=100, seed=20261116):
    """Permute within page+block, preserving physical positions and missing gaps.

    Synthetic fixture only. Does not implement the locked W47 scientific runner.
    """
    if not (isinstance(repeats, int) and repeats > 0):
        raise ValueError("Invalid repeats")
    rng = random.Random(seed)
    groups = defaultdict(list)
    for row in rows:
        groups[(row["page"], row["block"])].append(dict(row))
    outputs = []
    for _ in range(repeats):
        shuffled = []
        for lines in groups.values():
            words = [r["word"] for r in lines]
            rng.shuffle(words)
            shuffled.extend([dict(r, word=w) for r, w in zip(lines, words)])
        outputs.append(sum(a == b for a, b in eligible_pairs(shuffled)))
    return outputs


class SyntheticOnlyTests(unittest.TestCase):
    def test_no_bridge_over_missing_locus(self):
        rows = [
            dict(page="f1r", block=1, physical_line=1, word="abc"),
            dict(page="f1r", block=1, physical_line=3, word="abc"),
        ]
        self.assertEqual(eligible_pairs(rows), [])

    def test_no_cross_page_or_block(self):
        rows = [
            dict(page="f1r", block=1, physical_line=1, word="a"),
            dict(page="f1r", block=2, physical_line=2, word="a"),
            dict(page="f1v", block=1, physical_line=2, word="a"),
        ]
        self.assertEqual(eligible_pairs(rows), [])

    def test_exact_match_not_prefix(self):
        rows = [
            dict(page="f1r", block=1, physical_line=1, word="qo"),
            dict(page="f1r", block=1, physical_line=2, word="qoqo"),
            dict(page="f1r", block=1, physical_line=3, word="qoqo"),
        ]
        self.assertEqual(eligible_pairs(rows), [("qo", "qoqo"), ("qoqo", "qoqo")])

    def test_determinism_and_constant_words(self):
        rows = [dict(page="f1r", block=1, physical_line=i, word="same")
                for i in range(1, 5)]
        self.assertEqual(synthetic_permutation_counts(rows, 20),
                         synthetic_permutation_counts(rows, 20))
        self.assertEqual(synthetic_permutation_counts(rows, 20), [3] * 20)

    def test_duplicate_rejected(self):
        rows = [dict(page="f1r", block=1, physical_line=1, word="a")] * 2
        with self.assertRaises(ValueError):
            eligible_pairs(rows)


if __name__ == "__main__":
    unittest.main()
