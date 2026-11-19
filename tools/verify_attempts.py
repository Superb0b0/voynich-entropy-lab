#!/usr/bin/env python3
"""Fail-closed replay verifier for a custodian-prepared training-only bundle."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / "policy" / "legacy_attempt_exceptions.json"
PINNED_POLICY_SHA256 = "fe42da3f9302edcc653c106ce8dd3953280a4233d0e38d53a17b637dd0878b1f"
NUM = re.compile(r"^[0-9a-f]{64}$")
ATTEMPT = re.compile(r"^[0-9]{3}-[^/]+$")
# Issue #27: the first 008 result was committed before its protocol.
ARCHIVED_008 = "008-depend-firstclass-reuse"


def fail(message):
    raise RuntimeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def validate_training_bundle(data_dir):
    data_dir = pathlib.Path(data_dir).resolve()
    bundle_path = data_dir / "training_manifest.json"
    if not bundle_path.is_file():
        fail("training_manifest.json missing; no prepared training-only bundle")
    try:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        fail("training_manifest.json is invalid")
    required = {
        "schema", "schema_version", "policy_manifest_sha256",
        "source_holdout_blob_sha1", "source_corpus_sha256",
        "training_corpus_sha256", "filtered_page_block_counts",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        fail("training bundle schema keys are invalid")
    if bundle["schema"] != "voynich-training-only-bundle" or bundle["schema_version"] != 1:
        fail("unsupported training bundle schema")
    if bundle["policy_manifest_sha256"] != PINNED_POLICY_SHA256:
        fail("training bundle was prepared from an unreviewed policy manifest")
    if not re.fullmatch(r"[0-9a-f]{40}", str(bundle["source_holdout_blob_sha1"])):
        fail("training bundle source provenance is malformed")
    source_hashes = bundle["source_corpus_sha256"]
    training_hashes = bundle["training_corpus_sha256"]
    counts = bundle["filtered_page_block_counts"]
    if not isinstance(source_hashes, dict) or not source_hashes:
        fail("training bundle source corpus list is invalid")
    if not isinstance(training_hashes, dict) or set(training_hashes) != set(source_hashes):
        fail("training bundle corpus hash sets differ")
    if not isinstance(counts, dict) or set(counts) != set(source_hashes):
        fail("training bundle filtered-count keys differ")
    if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+\.txt", name) for name in source_hashes):
        fail("training bundle contains an invalid corpus filename")
    if any(not isinstance(value, str) or not NUM.fullmatch(value) for value in source_hashes.values()):
        fail("training bundle source corpus digest is invalid")
    if any(not isinstance(value, str) or not NUM.fullmatch(value) for value in training_hashes.values()):
        fail("training bundle training corpus digest is invalid")
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 1 for value in counts.values()):
        fail("training bundle must record removed protected page blocks")
    actual_files = {p.name for p in data_dir.glob("*.txt")}
    if actual_files != set(training_hashes):
        fail("training bundle file set differs from its manifest")
    for name, expected in training_hashes.items():
        if sha256((data_dir / name).read_bytes()) != expected:
            fail(f"training bundle SHA-256 mismatch: {name}")
    return bundle


def compare(expected, actual, tolerance, path="$"):
    if isinstance(expected, bool) or isinstance(actual, bool):
        if type(expected) is not type(actual) or expected != actual:
            fail(f"{path}: boolean mismatch")
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        import math
        if not math.isfinite(expected) or not math.isfinite(actual) or abs(expected - actual) > tolerance:
            fail(f"{path}: {expected} vs {actual}, tolerance={tolerance}")
    elif isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected) != set(actual):
            fail(f"{path}: keys differ")
        for key in expected:
            compare(expected[key], actual[key], tolerance, path + "." + str(key))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            fail(f"{path}: lengths differ")
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, tolerance, f"{path}[{index}]")
    elif expected != actual:
        fail(f"{path}: mismatch")


def load_legacy_exceptions():
    try:
        doc = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        fail("legacy exception register is missing or invalid")
    if not isinstance(doc, dict) or set(doc) != {"schema", "schema_version", "exceptions"}:
        fail("legacy exception register schema is invalid")
    if doc["schema"] != "voynich-legacy-attempt-exceptions" or doc["schema_version"] != 1:
        fail("unsupported legacy exception register")
    entries = doc["exceptions"]
    if not isinstance(entries, list):
        fail("legacy exception list is invalid")
    result = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "attempt_id", "status", "recorded_on", "reason", "evidence"
        }:
            fail("legacy exception record schema is invalid")
        name = entry["attempt_id"]
        if not isinstance(name, str) or not ATTEMPT.fullmatch(name):
            fail("legacy exception attempt id is invalid")
        if entry["status"] != "NOT_VERIFIABLE_LEGACY":
            fail(f"{name}: only NOT_VERIFIABLE_LEGACY is accepted")
        if not isinstance(entry["reason"], str) or not entry["reason"].strip():
            fail(f"{name}: exception requires a reason")
        if not isinstance(entry["evidence"], list) or not entry["evidence"]:
            fail(f"{name}: exception requires evidence references")
        if name in result:
            fail(f"{name}: duplicate legacy exception")
        result[name] = entry
    return result


def verify_attempt(folder, safe_dir, forbidden):
    cfg_path = folder / "attempt.yml"
    if not cfg_path.is_file():
        fail(f"{folder.name}: missing attempt.yml; cannot infer execution contract")
    try:
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError):
        fail(f"{folder.name}: invalid attempt.yml")
    if not isinstance(cfg, dict):
        fail(f"{folder.name}: invalid attempt.yml")
    seed = cfg.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        fail(f"{folder.name}: explicit integer seed required")
    tolerance = cfg.get("tolerance")
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance < 0:
        fail(f"{folder.name}: nonnegative numeric tolerance required")
    command = cfg.get("command")
    if command is None:
        if not (folder / "run.sh").is_file():
            fail(f"{folder.name}: missing run.sh and command")
        command = ["bash", "run.sh"]
    elif isinstance(command, str):
        command = shlex.split(command)
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        fail(f"{folder.name}: command must be a nonempty string or argv list")
    expected = folder / "results.json"
    if not expected.is_file():
        fail(f"{folder.name}: missing committed results.json")
    output = folder / "results_ci.json"
    output.unlink(missing_ok=True)
    env = {key: value for key, value in os.environ.items() if key != "VOY_HOLDOUT_HMAC_KEY"}
    env.update({
        "PYTHONHASHSEED": str(seed),
        "VOYNICH_SEED": str(seed),
        "VOYNICH_DATA_DIR": str(safe_dir),
        "VOYNICH_HOLDOUT_POLICY": "TRAIN_ONLY",
    })
    with tempfile.TemporaryDirectory() as temp_dir:
        trace = pathlib.Path(temp_dir) / "trace"
        run = subprocess.run(
            [
                "strace", "-f", "-qq",
                "-e", "trace=open,openat,openat2,readlink,readlinkat",
                "-s", "4096", "-o", str(trace), "--", *command,
            ],
            cwd=folder, env=env, timeout=600, capture_output=True, text=True,
        )
        log = trace.read_text(errors="replace")
        for raw_path in re.findall(r'(?:open|openat|openat2|readlink|readlinkat)\([^\n]*?"([^"\n]+)"', log):
            candidate = (folder / raw_path).resolve() if not os.path.isabs(raw_path) else pathlib.Path(raw_path).resolve()
            if candidate in forbidden or candidate.name == "HOLDOUT.md":
                fail(f"{folder.name}: protected input access attempt detected")
        if run.returncode:
            fail(f"{folder.name}: command failed ({run.returncode}): {run.stderr[-1200:]}")
    if not output.is_file():
        fail(f"{folder.name}: no results_ci.json produced")
    try:
        compare(json.loads(expected.read_text(encoding="utf-8")),
                json.loads(output.read_text(encoding="utf-8")), tolerance)
    except (UnicodeDecodeError, json.JSONDecodeError):
        fail(f"{folder.name}: result JSON is invalid")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    args = parser.parse_args(argv)
    summary_path = ROOT / "verification_summary.json"
    summary_path.unlink(missing_ok=True)
    bundle = validate_training_bundle(args.data_dir)
    if shutil.which("strace") is None:
        fail("strace unavailable; cannot audit reads")
    attempts = sorted(
        path for path in (ROOT / "attempts").glob("*")
        if path.is_dir() and ATTEMPT.fullmatch(path.name)
    )
    if not attempts:
        fail("No attempts/NNN-*/ found; verification is NOT VERIFIED")
    exceptions = load_legacy_exceptions()
    attempt_names = {path.name for path in attempts}
    if set(exceptions) - attempt_names:
        fail("legacy exception references an attempt directory that is absent")
    if ARCHIVED_008 in exceptions:
        fail(f"{ARCHIVED_008}: this archive requires replay and cannot be a legacy exception")
    verified = []
    not_verifiable = []
    technical_replays = []
    safe_dir = pathlib.Path(args.data_dir).resolve()
    forbidden = {
        (ROOT / "data" / name).resolve()
        for name in bundle["source_corpus_sha256"]
    }
    for folder in attempts:
        if folder.name.startswith("008-") and folder.name != ARCHIVED_008:
            fail(f"{folder.name}: unrecognized archive for reserved attempt 008")
        exception = exceptions.get(folder.name)
        if exception:
            if (folder / "attempt.yml").exists():
                fail(f"{folder.name}: legacy exception is obsolete because attempt.yml exists")
            not_verifiable.append(folder.name)
            continue
        verify_attempt(folder, safe_dir, forbidden)
        if folder.name == ARCHIVED_008:
            technical_replays.append({
                "attempt_id": folder.name,
                "replay_status": "REPRODUCED",
                "preregistration_status": "NOT_ATTESTABLE_FROM_ARCHIVE",
            })
        else:
            verified.append(folder.name)
    summary = {
        "schema": "voynich-attempt-verification-summary",
        "schema_version": 1,
        "status": (
            "NOT_VERIFIED_NO_ACTIVE_ATTEMPTS" if not verified else
            "VERIFIED_WITH_EXPLICIT_LEGACY_EXCEPTION" if not_verifiable else
            "VERIFIED"
        ),
        "verified_attempts": verified,
        "not_verifiable_legacy": not_verifiable,
        "training_bundle_policy_manifest_sha256": bundle["policy_manifest_sha256"],
    }
    if technical_replays:
        summary["technical_replays"] = technical_replays
        print(f"Technical replay reproduced: {ARCHIVED_008}. Preregistration not attestable from the archive.")
    summary_path.write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    if not verified:
        fail("No active attempt was replayed. See the summary for legacy exceptions and technical replays.")
    if not_verifiable:
        print(f"VERIFIED_WITH_EXPLICIT_LEGACY_EXCEPTION: {len(verified)} replayed; {len(not_verifiable)} not verifiable legacy")
    else:
        print(f"VERIFIED: {len(verified)} attempts replayed; training-only bundle hash checks passed")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError, OSError) as exc:
        print(f"NON VERIFICATO: {exc}", file=sys.stderr)
        sys.exit(1)
