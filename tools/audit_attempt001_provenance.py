#!/usr/bin/env python3
"""Read-only provenance audit of historical attempt 001; NEVER runs the experiment."""
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMIT = "0e87d9758f288cdeac29513ee04245dcd8126592"
BASE = "attempts/001-paragraph-header-key"
FILES = ("run.py", "manifest.json", "results.json")

def main():
    manifest = json.loads((ROOT / BASE / "manifest.json").read_text())
    if manifest["status"] != "ESPLORATIVO":
        raise RuntimeError("unexpected historical status")
    for name in FILES:
        path = f"{BASE}/{name}"
        historical = subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=ROOT)
        current = (ROOT / path).read_bytes()
        if current != historical:
            raise RuntimeError(f"historical archive diverged: {path}")
        print(f"ARCHIVE MATCH {path}: sha256={hashlib.sha256(current).hexdigest()}")
    script_hash = hashlib.sha256((ROOT / BASE / "run.py").read_bytes()).hexdigest()
    if script_hash != manifest["executed_script_sha256"]:
        raise RuntimeError("executed script hash mismatch")
    source = (ROOT / BASE / "run.py").read_text()
    if manifest["inputs"]["corpus"]["sha256"] not in source:
        raise RuntimeError("corpus hash lock missing from original script")
    if manifest["inputs"]["parser"]["sha256"] not in source:
        raise RuntimeError("parser hash lock missing from original script")
    if "assert len(records) == 4130" not in source:
        raise RuntimeError("original full-corpus record expectation absent")
    print("PROVENANCE PASS: original archived source, manifest and results unchanged")
    print("REPLAY NOT PERFORMED: historical script requires full corpus; holdout sealed")
    print("STATUS: HISTORICAL PROVENANCE ATTESTED; REPRODUCIBILITY NOT VERIFIED")

if __name__ == "__main__":
    main()
