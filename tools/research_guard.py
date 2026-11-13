#!/usr/bin/env python3
"""Fail-closed repository integrity and holdout guard. No held-out content is opened."""
import hashlib
from pathlib import Path

EXPECTED = {
    "data/ZL3b-n.txt": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "data/IT2a-n.txt": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
}
HELDOUT_LEAVES = frozenset({2,5,9,17,31,32,36,37,38,45,48,49,67,69,78,85,86,94,95,101,111})
for name, expected in EXPECTED.items():
    path = Path(name)
    if not path.is_file():
        raise SystemExit(f"BLOCKED missing corpus: {name}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"BLOCKED checksum mismatch: {name}")
if not Path("HOLDOUT.md").is_file():
    raise SystemExit("BLOCKED: missing HOLDOUT.md")
print("PASS: corpus hashes verified; held-out leaves must not be accessed.")
