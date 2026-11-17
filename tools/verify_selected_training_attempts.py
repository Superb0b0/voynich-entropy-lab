#!/usr/bin/env python3
"""Replay only pinned exploratory attempts against a pinned training-only bundle.

This is a technical reproducibility check, not a new scientific experiment.
It never calls verifier.hashes() or verifier.protected().
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys

PINS = {
    "005-refractory-qo-parameter": {
        "corpus": "ZL3b-n.txt",
        "training_sha256": "dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9",
        "run_py_sha256": "c522868b488707d8fe87e5a1d78683e29de28e9663c6eb1144d232f773e0118e",
        "results_sha256": "1dc84f8a7a6225281fd64726e10a5ef201a23523382f88baa93534e22e9607af",
        "run_sh_sha256": "faeeeba4e392b91941aa461f59308644171add8e84b03c3619de4e55e04b4c24",
    },
    "006-it2a-replication": {
        "corpus": "IT2a-n.txt",
        "training_sha256": "a12879dfa02f8fc8f9a9c9a9bea5bf019283959ceca09a446abdd273baced9705c",
        "run_py_sha256": "c522868b488707d8fe87e5a1d78683e29de28e9663c6eb1144d232f773e0118e",
        "results_sha256": "31a2735d63d46b2ca38889b9583e7a5d492336c3869bb86c4bf0393445345c6f",
        "run_sh_sha256": "b29cded3a477e1aaf953f426b425f638e6f4348299ccd398f98699a77182d5ed",
    },
}
POLICY_SHA256 = "fe42da3f9302edcc653c106ce8dd3953280a4233d0e38d53a17b637dd0878b1f"
SOURCE_HASHES = {
    "ZL3b-n.txt": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "IT2a-n.txt": "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=pathlib.Path)
    ap.add_argument("--data-dir", required=True, type=pathlib.Path)
    ap.add_argument("--verifier", required=True, type=pathlib.Path)
    args = ap.parse_args()

    root = args.root.resolve()
    data_dir = args.data_dir.resolve()
    verifier_path = args.verifier.resolve()
    require(not (root / "HOLDOUT.md").exists(), "PR checkout unexpectedly contains HOLDOUT.md")
    require(not (root / "data").exists(), "PR checkout unexpectedly contains canonical data/")
    require(not (verifier_path.parents[1] / "HOLDOUT.md").exists(),
            "reviewed verifier checkout unexpectedly contains HOLDOUT.md")
    require(data_dir.is_dir(), "training-only bundle directory missing")

    bundle_manifest_path = data_dir / "training_manifest.json"
    bundle = json.loads(bundle_manifest_path.read_text(encoding="utf-8"))
    require(bundle.get("schema") == "voynich-training-only-bundle", "unexpected bundle schema")
    require(bundle.get("schema_version") == 1, "unexpected bundle schema version")
    require(bundle.get("policy_manifest_sha256") == POLICY_SHA256, "policy manifest digest mismatch")
    require(bundle.get("source_corpus_sha256") == SOURCE_HASHES, "source corpus pins mismatch")
    require(bundle.get("filtered_page_block_counts") == {"IT2a-n.txt": 48, "ZL3b-n.txt": 48},
            "filtered block counts mismatch")

    for corpus, expected in {
        "ZL3b-n.txt": PINS["005-refractory-qo-parameter"]["training_sha256"],
        "IT2a-n.txt": PINS["006-it2a-replication"]["training_sha256"],
    }.items():
        path = data_dir / corpus
        require(path.is_file(), f"training corpus absent: {corpus}")
        actual = sha256(path)
        require(actual == expected, f"training corpus digest mismatch: {corpus}")
        require(bundle.get("training_corpus_sha256", {}).get(corpus) == expected,
                f"bundle manifest digest mismatch: {corpus}")
        print(f"TRAINING_BUNDLE_HASH_PASS {corpus} {actual}")

    spec = importlib.util.spec_from_file_location("pinned_verify_attempts", verifier_path)
    require(spec is not None and spec.loader is not None, "cannot load pinned verifier")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    require(callable(getattr(verifier, "verify_attempt", None)), "pinned verifier lacks verify_attempt")

    # These are path guards only. No protected file is opened or read.
    forbidden = {
        (root / "data" / corpus).resolve()
        for corpus in ("ZL3b-n.txt", "IT2a-n.txt")
    }
    forbidden.add(verifier.HOLDOUT.resolve())

    for name, pin in PINS.items():
        folder = root / "attempts" / name
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        require(manifest.get("attempt") == name, f"{name}: attempt identity mismatch")
        require(manifest.get("corpus") == pin["corpus"], f"{name}: corpus identity mismatch")
        require(manifest.get("corpus_full_sha256_expected") == SOURCE_HASHES[pin["corpus"]],
                f"{name}: canonical corpus pin mismatch")
        require(manifest.get("corpus_training_only_sha256") == pin["training_sha256"],
                f"{name}: training corpus pin mismatch")
        require(manifest.get("run_py_sha256") == pin["run_py_sha256"],
                f"{name}: run.py manifest pin mismatch")
        require(manifest.get("results_json_sha256") == pin["results_sha256"],
                f"{name}: results manifest pin mismatch")
        require(manifest.get("seed") == 20261121, f"{name}: seed mismatch")
        require(sha256(folder / "run.py") == pin["run_py_sha256"], f"{name}: run.py digest mismatch")
        require(sha256(folder / "run.sh") == pin["run_sh_sha256"], f"{name}: run.sh digest mismatch")
        require(sha256(folder / "results.json") == pin["results_sha256"],
                f"{name}: committed results digest mismatch")
        cfg = verifier.yaml.safe_load((folder / "attempt.yml").read_text(encoding="utf-8"))
        require(cfg == {"seed": 20261121, "tolerance": 0.000001, "command": ["bash", "run.sh"]},
                f"{name}: execution contract mismatch")
        verifier.verify_attempt(folder, data_dir, forbidden)
        print(f"TECHNICAL_REPLAY_PASS {name}")

    print("TECHNICAL_REPLAY_COMPLETE: only pinned attempts 005/006; no holdout read; no new scientific claim")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"TECHNICAL_REPLAY_NOT_VERIFIED: {exc}", file=sys.stderr)
        sys.exit(1)
