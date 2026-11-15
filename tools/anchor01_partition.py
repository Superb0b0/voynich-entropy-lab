"""Deterministic folio-group partition of already attested eligible page IDs.

This module never opens corpus or policy files.
"""
import hashlib
import json
import re

PAGE = re.compile(r"^f(\d+)[rv]\d*$")
SEED = "VOY-ANCHOR-01-20261115-v1"

def partition(eligible_page_ids, test_fraction=0.25):
    pages = list(eligible_page_ids)
    if not pages or len(pages) != len(set(pages)):
        raise ValueError("empty or duplicate eligible pages")
    if not 0 < test_fraction < 1:
        raise ValueError("invalid test fraction")
    groups = {}
    for page in pages:
        m = PAGE.fullmatch(page)
        if m is None:
            raise ValueError("invalid page ID")
        groups.setdefault(int(m.group(1)), []).append(page)
    if len(groups) < 4:
        raise ValueError("insufficient folio groups")
    ordered = sorted(groups, key=lambda k: hashlib.sha256(f"{SEED}:{k}".encode()).digest())
    test_count = max(1, round(len(ordered) * test_fraction))
    test = set(ordered[:test_count])
    discovery = sorted(p for k, ps in groups.items() if k not in test for p in ps)
    held_test = sorted(p for k, ps in groups.items() if k in test for p in ps)
    assert set(discovery).isdisjoint(held_test)
    return {
        "schema": "voy-anchor01-folio-split-v1",
        "seed": SEED,
        "method": "sha256(seed:folio_number) ascending, first round(25%) groups to internal test",
        "discovery_page_ids": discovery,
        "internal_test_page_ids": held_test,
        "discovery_folio_count": len(groups) - test_count,
        "internal_test_folio_count": test_count,
        "source_eligible_sha256": hashlib.sha256(json.dumps(sorted(pages), separators=(",", ":")).encode()).hexdigest(),
    }
