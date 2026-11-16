#!/usr/bin/env python3
"""Synthetic-only IVTFF boundary auditor for W47. Never reads corpus/holdout.

Not a replacement for RC1.2. Does not attest the historical 740 count.
Ambiguous/unfinished blocks are quarantined rather than silently accepted.
"""
import re
import unittest

HEADER = re.compile(r"^<([^>]+)>[ \t]*(.*)$")
START, END = "<%>", "<$>"


def audit_boundaries(lines):
    blocks, errors = [], []
    active = None
    page = None

    def close(reason, end_line=None):
        nonlocal active
        if active is not None:
            active["closure"] = reason
            active["end_physical_line"] = end_line
            active["status"] = "complete" if reason == "end_marker" else "incomplete"
            blocks.append(active)
            active = None

    for physical_line, raw in enumerate(lines, 1):
        m = HEADER.match(raw)
        if not m or "," not in m.group(1):
            continue
        locus, tag = m.group(1).split(",", 1)
        locus_page = locus.rsplit(".", 1)[0]
        if page != locus_page:
            close("page_change", physical_line - 1)
            page = locus_page
        body = m.group(2)
        if START in body and END in body and body.index(END) < body.index(START):
            errors.append({"physical_line": physical_line, "reason": "end_before_start"})
            close("ambiguous_order", physical_line)
            continue
        if body.count(START) > 1 or body.count(END) > 1:
            errors.append({"physical_line": physical_line, "reason": "multiple_markers"})
            close("ambiguous_markers", physical_line)
            continue
        if START in body:
            close("new_start_without_end", physical_line - 1)
            active = {"page": page, "start_locus": locus,
                      "start_physical_line": physical_line, "loci": []}
        if active is not None:
            active["loci"].append({"locus": locus, "tag": tag,
                                   "physical_line": physical_line})
        if END in body:
            if active is None:
                errors.append({"physical_line": physical_line, "reason": "orphan_end"})
            else:
                close("end_marker", physical_line)
    close("eof", len(lines))
    return {"blocks": blocks, "errors": errors}


class SyntheticBoundaryTests(unittest.TestCase):
    def test_complete_and_intercalated_non_p(self):
        rows = ["<f1r.1,+P0> a<%>", "<f1r.2,@L0> label",
                "<f1r.3,+P0> b<$>"]
        out = audit_boundaries(rows)
        self.assertEqual(len(out["blocks"]), 1)
        self.assertEqual(out["blocks"][0]["status"], "complete")
        self.assertEqual(len(out["blocks"][0]["loci"]), 3)

    def test_page_reset(self):
        out = audit_boundaries(["<f1r.1,+P0> a<%>",
                                "<f1v.1,+P0> b<$>"])
        self.assertEqual(out["blocks"][0]["closure"], "page_change")
        self.assertEqual(out["errors"][0]["reason"], "orphan_end")

    def test_new_start_closes_incomplete(self):
        out = audit_boundaries(["<f1r.1,+P0> a<%>",
                                "<f1r.2,+P0> b<%>",
                                "<f1r.3,+P0> c<$>"])
        self.assertEqual([x["status"] for x in out["blocks"]],
                         ["incomplete", "complete"])

    def test_orphan_and_reversed(self):
        out = audit_boundaries(["<f1r.1,+P0> a<$>",
                                "<f1r.2,+P0> b<$><%>"])
        self.assertEqual([x["reason"] for x in out["errors"]],
                         ["orphan_end", "end_before_start"])

    def test_unclosed_eof(self):
        out = audit_boundaries(["<f1r.1,+P0> a<%>"])
        self.assertEqual(out["blocks"][0]["closure"], "eof")


if __name__ == "__main__":
    unittest.main()
