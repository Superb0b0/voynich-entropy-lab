#!/usr/bin/env python3
"""W47 synthetic-only structural manifest reconciliation; no corpus access.

This adapter refuses to certify parser parity. It joins an audited RC1.2
record stream to an independently supplied structural block manifest.
"""
from collections import Counter
import unittest


class MappingError(ValueError):
    pass


def reconcile(records, blocks):
    """Return auditable locus-to-block and eligible-pair manifests.

    RC1.2 records: locus_id, page, physical_line, line_index, tokens.
    Blocks: page, status, loci (each with locus, physical_line, tag).
    No inference from adjacent array indices. No silent handling of
    incomplete blocks or non-P intervening loci.
    """
    by_id = {}
    for r in records:
        locus = r["locus_id"]
        if locus in by_id:
            raise MappingError("duplicate canonical locus")
        if not r["tokens"]:
            raise MappingError("empty canonical tokens")
        by_id[locus] = r
    seen = set()
    locus_rows, pairs, quarantined = [], [], []
    for bi, block in enumerate(blocks):
        locs = block["loci"]
        if block["status"] != "complete":
            quarantined.append({"block_index": bi, "reason": "incomplete"})
            continue
        positions = [l["physical_line"] for l in locs]
        if positions != sorted(positions) or len(positions) != len(set(positions)):
            raise MappingError("unsorted or duplicate structural positions")
        mapped = []
        for loc in locs:
            lid = loc["locus"]
            if lid in seen:
                raise MappingError("locus in multiple blocks")
            seen.add(lid)
            r = by_id.get(lid)
            if r is None:
                if loc["tag"] in {"+P0", "+P1", "+Pb", "+Pc", "+Pr", "*P0", "*Pb", "=P0", "=Pt", "@P0", "@P1", "@Pb"}:
                    raise MappingError("missing canonical P locus")
                # Non-P loci remain structural barriers.
                mapped.append(None)
                continue
            if (r["page"] != block["page"] or
                    r["physical_line"] != loc["physical_line"]):
                raise MappingError("canonical/structural mismatch")
            mapped.append(r)
            locus_rows.append({"block_index": bi, "locus_id": lid,
                               "physical_line": r["physical_line"],
                               "token_count": len(r["tokens"])})
        for j in range(len(locs) - 1):
            left, right = mapped[j:j + 2]
            if left is None or right is None:
                continue
            if right["physical_line"] != left["physical_line"] + 1:
                continue
            if right["line_index"] != left["line_index"] + 1:
                continue
            pairs.append({"block_index": bi, "left": left["locus_id"],
                          "right": right["locus_id"]})
    return {"loci": locus_rows, "pairs": pairs, "quarantined": quarantined,
            "unmapped_canonical_count": len(set(by_id) -
                                            {r["locus_id"] for r in locus_rows})}


class SyntheticManifestTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            dict(locus_id="f1r.1", page="f1r", physical_line=1,
                 line_index=1, tokens=["a"]),
            dict(locus_id="f1r.3", page="f1r", physical_line=3,
                 line_index=3, tokens=["a"]),
            dict(locus_id="f1r.4", page="f1r", physical_line=4,
                 line_index=4, tokens=["a"]),
        ]

    def test_non_p_barrier(self):
        blocks = [dict(page="f1r", status="complete", loci=[
            dict(locus="f1r.1", physical_line=1, tag="+P0"),
            dict(locus="f1r.2", physical_line=2, tag="@L0"),
            dict(locus="f1r.3", physical_line=3, tag="+P0"),
            dict(locus="f1r.4", physical_line=4, tag="+P0")])]
        out = reconcile(self.records, blocks)
        self.assertEqual([(x["left"], x["right"]) for x in out["pairs"]],
                         [("f1r.3", "f1r.4")])

    def test_incomplete_quarantine(self):
        out = reconcile(self.records, [dict(page="f1r", status="incomplete",
                   loci=[dict(locus="f1r.1", physical_line=1, tag="+P0")])])
        self.assertEqual(out["pairs"], [])
        self.assertEqual(len(out["quarantined"]), 1)

    def test_mismatch_fail_closed(self):
        blocks = [dict(page="f1v", status="complete", loci=[
            dict(locus="f1r.1", physical_line=1, tag="+P0")])]
        with self.assertRaises(MappingError):
            reconcile(self.records, blocks)

    def test_duplicate_block_membership_rejected(self):
        block = dict(page="f1r", status="complete", loci=[
            dict(locus="f1r.1", physical_line=1, tag="+P0")])
        with self.assertRaises(MappingError):
            reconcile(self.records, [block, block])


if __name__ == "__main__":
    unittest.main()
