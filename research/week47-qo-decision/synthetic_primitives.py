"""Synthetic-only W47 adjacency and permutation primitives.

No corpus IO, no GitHub access, no holdout access, and NO scientific runner.
A future locked runner must supply independently audited RC1.2 records.
"""
from collections import defaultdict
import random


def eligible_pairs(lines):
    """Yield immediately adjacent physical P lines in the same page/block.

    Each record: page, block, locus_index (physical sequential index),
    first_word (nonempty string), folio. Never bridge a missing locus.
    """
    for left, right in zip(lines, lines[1:]):
        if (left["page"] == right["page"]
                and left["block"] == right["block"]
                and right["locus_index"] == left["locus_index"] + 1
                and left["first_word"] and right["first_word"]):
            yield left, right


def repeat_count(lines):
    return sum(a["first_word"] == b["first_word"]
               for a, b in eligible_pairs(lines))


def permutation_counts(lines, *, replicates=10000, seed=20261116):
    """Within-block shuffle of first words; preserve physical loci and gaps."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    groups = defaultdict(list)
    for index, line in enumerate(lines):
        if line["first_word"]:
            groups[(line["page"], line["block"])].append(index)
    rng = random.Random(seed)
    result = []
    for _ in range(replicates):
        words = [dict(x) for x in lines]
        for indices in groups.values():
            values = [lines[i]["first_word"] for i in indices]
            rng.shuffle(values)
            for i, word in zip(indices, values):
                words[i]["first_word"] = word
        result.append(repeat_count(words))
    return result


if __name__ == "__main__":
    # Synthetic fixtures only: gaps and boundaries must never create pairs.
    rows = [
        dict(page="p1", block="b1", locus_index=1, first_word="aa", folio="f1"),
        dict(page="p1", block="b1", locus_index=2, first_word="aa", folio="f1"),
        dict(page="p1", block="b1", locus_index=4, first_word="aa", folio="f1"),
        dict(page="p1", block="b2", locus_index=5, first_word="aa", folio="f1"),
        dict(page="p2", block="b2", locus_index=6, first_word="aa", folio="f2"),
    ]
    assert len(list(eligible_pairs(rows))) == 1
    assert repeat_count(rows) == 1
    assert permutation_counts(rows, replicates=20) == [1] * 20
    rows[1]["first_word"] = "bb"
    assert repeat_count(rows) == 0
    assert permutation_counts(rows, replicates=20, seed=3) == permutation_counts(rows, replicates=20, seed=3)
    print("PASS: synthetic boundaries, gaps, identity and deterministic replay")
