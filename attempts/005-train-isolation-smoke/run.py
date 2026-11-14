#!/usr/bin/env python3
"""Engineering-only train-split smoke test; no scientific inference."""
import hashlib
import json
import os
from pathlib import Path

def main():
    folder = Path(__file__).resolve().parent
    data_dir = Path(os.environ["VOYNICH_DATA_DIR"])
    corpus = (data_dir / "ZL3b-n.txt").read_bytes()
    # Intentionally do not read data/, HOLDOUT.md or full-corpus manifests.
    output = {
        "classification": "ENGINEERING_SMOKE_TEST",
        "train_sha256": hashlib.sha256(corpus).hexdigest(),
        "train_bytes": len(corpus),
        "train_lines": len(corpus.splitlines()),
        "seed": int(os.environ["VOYNICH_SEED"]),
        "scientific_claim": False,
    }
    (folder / "results_ci.json").write_text(
        json.dumps(output, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )

if __name__ == "__main__":
    main()
