#!/usr/bin/env python3
"""Deterministic qo training-only CI; never opens or copies HOLDOUT.md."""
import hashlib
import importlib.util
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
FILENAME = "ZL3b-n.txt"


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def protect_workspace(stage):
    if (ROOT / "HOLDOUT.md").exists():
        raise RuntimeError(f"{stage}: HOLDOUT.md present; refuse to run")


def prepare():
    protect_workspace("prepare")
    q = load("qo_calibration_prep", "tools/qo_rival_calibration.py")
    original = ROOT / "data" / FILENAME
    raw = original.read_bytes()
    if sha_bytes(raw) != EXPECTED:
        raise RuntimeError("source SHA-256 mismatch")
    # Read only the IVTFF page header to select pages; no protected text is evaluated.
    kept = []
    current_leaf = None
    pages = kept_pages = 0
    for line in raw.decode("utf-8").splitlines(keepends=True):
        match = q.PAGE.match(line)
        if match:
            pages += 1
            current_leaf = int(match.group(2))
            if current_leaf not in q.HELD:
                kept_pages += 1
        if current_leaf is not None and current_leaf not in q.HELD:
            kept.append(line)
    if pages < 1 or kept_pages < 1 or kept_pages >= pages:
        raise RuntimeError("invalid training/holdout page split")
    training = "".join(kept).encode("utf-8")
    safe = ROOT / "training-snapshot" / "data" / FILENAME
    safe.parent.mkdir(parents=True, exist_ok=True)
    safe.write_bytes(training)
    for line in safe.read_text(encoding="utf-8").splitlines():
        match = q.PAGE.match(line)
        if match and int(match.group(2)) in q.HELD:
            raise RuntimeError("protected page in training snapshot")
    dump(ROOT / "training-snapshot" / "report" / "input-manifest.json", {
        "original_sha256": EXPECTED,
        "training_sha256": sha_bytes(training),
        "source_bytes": len(raw),
        "training_bytes": len(training),
        "pages_total": pages,
        "pages_training": kept_pages,
        "protected_file_checked_out": False,
        "classification": "training-only input, not independent holdout validation",
    })
    print("PASS: original hash checked and training-only artifact prepared")


def analyze():
    protect_workspace("analysis")
    if (ROOT / "data" / FILENAME).exists():
        raise RuntimeError("full original corpus present in analysis workspace")
    manifest_path = ROOT / "training-snapshot" / "report" / "input-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    safe = ROOT / "training-snapshot" / "data" / FILENAME
    raw = safe.read_bytes()
    digest = sha_bytes(raw)
    if manifest.get("original_sha256") != EXPECTED or digest != manifest.get("training_sha256"):
        raise RuntimeError("training snapshot provenance mismatch")

    q = load("qo_rival_calibration_runner", "tools/qo_rival_calibration.py")
    for line in raw.decode("utf-8").splitlines():
        match = q.PAGE.match(line)
        if match and int(match.group(2)) in q.HELD:
            raise RuntimeError("protected page detected in training artifact")
    q.SOURCE, q.SHA = safe, digest
    q.main()
    first = json.loads((ROOT / "research-output" / "qo-rival.json").read_text())
    q.main()
    second = json.loads((ROOT / "research-output" / "qo-rival.json").read_text())
    first.pop("generated_at", None)
    second.pop("generated_at", None)
    if first != second:
        raise RuntimeError("qo replay is not deterministic")

    c = load("qo_circular_runner", "tools/qo_rival_circular_shift.py")
    c.qo.SOURCE, c.qo.SHA = safe, digest
    c.main()
    circular_first = (ROOT / "research-output" / "qo-rival-circular-shift.json").read_bytes()
    c.main()
    circular_second = (ROOT / "research-output" / "qo-rival-circular-shift.json").read_bytes()
    if circular_first != circular_second:
        raise RuntimeError("circular-shift replay is not deterministic")

    passes = all(v["holm_2"] <= 0.01 for v in first["null_models"].values())
    status = "eseguito: confermato" if passes else "eseguito: falsificato"
    execution = {
        "status": status,
        "status_scope": "Only the prespecified two-shuffle training comparison",
        "scientific_status": "EXPLORATORY_NOT_VALIDATED",
        "reproduced_identically_twice": True,
        "input_sha256_original": EXPECTED,
        "input_sha256_training": digest,
        "workflow_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "seed": q.SEED,
        "permutations_per_shuffling_rival": q.REPS,
        "additional_circular_shift_model": "diagnostic only; not part of the two-null death criterion",
        "pipeline": "read-only sparse checkout, protected-page exclusion, isolated training artifact",
        "warning": "A passing training comparison is not a Voynich decipherment or independent confirmation",
    }
    dump(ROOT / "research-output" / "EXECUTION.json", execution)
    dump(ROOT / "research-output" / "training-input-manifest.json", manifest)
    print("RESULT:", status, "(training-only, no scientific validation)")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("prepare", "analyze"):
        raise SystemExit("Usage: qo_isolated_runner.py prepare|analyze")
    stage = sys.argv[1]
    try:
        (prepare if stage == "prepare" else analyze)()
    except Exception as exc:
        output = ROOT / ("training-snapshot/report" if stage == "prepare" else "research-output") / "EXECUTION_ERROR.json"
        dump(output, {"status": "non eseguito: causa tecnica", "stage": stage,
                      "reason": str(exc)[:300]})
        raise


if __name__ == "__main__":
    main()
