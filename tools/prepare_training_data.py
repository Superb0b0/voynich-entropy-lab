#!/usr/bin/env python3
"""Create a training-only bundle from public corpora using a custodian HMAC manifest.

This trusted preprocessing step never opens HOLDOUT.md. It reads the canonical
corpus files and the HMAC manifest, filters complete IVTFF page blocks, and
writes only the filtered corpus plus non-identifying provenance metadata.
"""
import argparse
import hashlib
import hmac
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
POLICY_MANIFEST = ROOT / "policy" / "holdout_page_hmac_manifest.json"
CANONICAL_MANIFEST = ROOT / "MANIFEST.md"
DATA_DIR = ROOT / "data"
PINNED_POLICY_SHA256 = "fe42da3f9302edcc653c106ce8dd3953280a4233d0e38d53a17b637dd0878b1f"
EXPECTED_SCHEMA = "voynich-protected-page-hmac-manifest"
EXPECTED_NORMALIZATION = "exact case-sensitive capture; no additional normalization; deduplicated"
EXPECTED_PATTERN = r"['\"](f\d+[rv]\d*)['\"]"
PAGE_HEADER = re.compile(r"^<(f\d+[rv]\d*)>\s+<!")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def fail(message):
    raise RuntimeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def expected_corpus_hashes():
    expected = {}
    for line in CANONICAL_MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.fullmatch(r"data/[^/]+\.txt", cells[0]) and HEX64.fullmatch(cells[2]):
            expected[cells[0].split("/", 1)[1]] = cells[2]
    if not expected:
        fail("MANIFEST.md contains no machine-readable corpus hashes")
    return expected


def current_holdout_blob_sha():
    # Read Git tree metadata only; do not checkout, open, or read the blob.
    result = subprocess.run(
        ["git", "ls-tree", "HEAD", "--", "HOLDOUT.md"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    match = re.fullmatch(r"\d+ blob ([0-9a-f]{40})\tHOLDOUT\.md\n?", result.stdout)
    if not match:
        fail("HOLDOUT.md blob metadata unavailable in current commit")
    return match.group(1)


def load_policy_manifest(key_bytes, manifest_path=POLICY_MANIFEST, expected_sha256=PINNED_POLICY_SHA256):
    raw = pathlib.Path(manifest_path).read_bytes()
    digest = sha256(raw)
    if expected_sha256 and not hmac.compare_digest(digest, expected_sha256):
        fail("Custodian manifest SHA-256 differs from the reviewed pin")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        fail("Custodian manifest is not valid UTF-8 JSON")
    if not isinstance(doc, dict) or set(doc) != {
        "schema", "schema_version", "algorithm", "normalization",
        "identifier_pattern", "source", "identifier_count", "hmac_sha256"
    }:
        fail("Custodian manifest schema keys are invalid")
    if doc["schema"] != EXPECTED_SCHEMA or doc["schema_version"] != 1:
        fail("Unsupported custodian manifest schema")
    if doc["algorithm"] != "HMAC-SHA-256":
        fail("Unsupported custodian manifest algorithm")
    if doc["normalization"] != EXPECTED_NORMALIZATION or doc["identifier_pattern"] != EXPECTED_PATTERN:
        fail("Custodian manifest identifier rule differs from the reviewed rule")
    source = doc["source"]
    if not isinstance(source, dict) or set(source) != {"path", "commit", "git_blob_sha1", "file_sha256"}:
        fail("Custodian manifest source metadata is invalid")
    if source["path"] != "HOLDOUT.md" or not HEX40.fullmatch(str(source["commit"])):
        fail("Custodian manifest source reference is invalid")
    if not HEX40.fullmatch(str(source["git_blob_sha1"])) or not HEX64.fullmatch(str(source["file_sha256"])):
        fail("Custodian manifest source digests are invalid")
    if not hmac.compare_digest(current_holdout_blob_sha(), source["git_blob_sha1"]):
        fail("Current HOLDOUT.md blob metadata differs from the custodian source")
    values = doc["hmac_sha256"]
    if not isinstance(values, list) or not values or not all(isinstance(x, str) and HEX64.fullmatch(x) for x in values):
        fail("Custodian manifest HMAC entries are invalid")
    if values != sorted(set(values)) or doc["identifier_count"] != len(values):
        fail("Custodian manifest count, ordering, or uniqueness check failed")
    if len(key_bytes) < 32:
        fail("VOY_HOLDOUT_HMAC_KEY must contain at least 32 UTF-8 bytes")
    return set(values), digest


def sanitize_text(text, protected_hmacs, key_bytes):
    output = []
    skip_page = False
    saw_header = False
    matched_page_blocks = 0
    matched_hmacs = set()
    for line in text.splitlines(keepends=True):
        match = PAGE_HEADER.match(line)
        if match:
            saw_header = True
            digest = hmac.new(key_bytes, match.group(1).encode("utf-8"), hashlib.sha256).hexdigest()
            skip_page = digest in protected_hmacs
            if skip_page:
                matched_page_blocks += 1
                matched_hmacs.add(digest)
        if not skip_page:
            output.append(line)
    if not saw_header:
        fail("Corpus has no recognized IVTFF page headers")
    if matched_page_blocks == 0:
        fail("No protected pages matched; key, manifest, or corpus provenance is inconsistent")
    return "".join(output), matched_page_blocks, matched_hmacs


def require_manifest_coverage(protected_hmacs, observed_hmacs):
    missing = protected_hmacs - observed_hmacs
    if missing:
        fail(
            "Custodian manifest coverage incomplete: "
            f"{len(missing)} protected entries were not found across canonical corpora"
        )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    key_text = os.environ.get("VOY_HOLDOUT_HMAC_KEY", "")
    if not key_text:
        fail("VOY_HOLDOUT_HMAC_KEY is unavailable")
    key_bytes = key_text.encode("utf-8")
    protected_hmacs, policy_digest = load_policy_manifest(key_bytes)
    expected = expected_corpus_hashes()
    actual_paths = {p.name for p in DATA_DIR.glob("*.txt")}
    if actual_paths != set(expected):
        fail("Canonical corpus file set differs from MANIFEST.md")
    output_dir = pathlib.Path(args.output_dir).resolve()
    prepared = {}
    observed_hmacs = set()
    source_hashes = {}
    filtered_counts = {}
    for name in sorted(expected):
        source = DATA_DIR / name
        raw = source.read_bytes()
        source_digest = sha256(raw)
        if not hmac.compare_digest(source_digest, expected[name]):
            fail(f"Canonical corpus SHA-256 mismatch: {name}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            fail(f"Canonical corpus is not UTF-8: {name}")
        filtered, count, matched_hmacs = sanitize_text(text, protected_hmacs, key_bytes)
        filtered_bytes = filtered.encode("utf-8")
        if filtered_bytes == raw:
            fail(f"Sanitized corpus did not change: {name}")
        prepared[name] = filtered_bytes
        observed_hmacs.update(matched_hmacs)
        source_hashes[name] = source_digest
        filtered_counts[name] = count
    require_manifest_coverage(protected_hmacs, observed_hmacs)
    output_dir.mkdir(parents=True, exist_ok=True)
    training_hashes = {}
    for name, filtered_bytes in prepared.items():
        (output_dir / name).write_bytes(filtered_bytes)
        training_hashes[name] = sha256(filtered_bytes)
    bundle = {
        "schema": "voynich-training-only-bundle",
        "schema_version": 1,
        "policy_manifest_sha256": policy_digest,
        "source_holdout_blob_sha1": json.loads(POLICY_MANIFEST.read_text(encoding="utf-8"))["source"]["git_blob_sha1"],
        "source_corpus_sha256": source_hashes,
        "training_corpus_sha256": training_hashes,
        "filtered_page_block_counts": filtered_counts,
    }
    (output_dir / "training_manifest.json").write_text(
        json.dumps(bundle, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    # Do not print key material, protected identifiers, or corpus text.
    print(f"TRAINING_BUNDLE_PREPARED: {len(training_hashes)} corpora; protected blocks removed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        print(f"TRAINING_BUNDLE_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
