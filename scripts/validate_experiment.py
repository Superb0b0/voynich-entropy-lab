#!/usr/bin/env python3
"""Fail-closed V3.2 acceptance gate. Standard library only; never edits inputs."""
import argparse
import hashlib
import json
import pathlib
import sys

REQUIRED = ("experiment_id", "hypothesis", "falsifiable_prediction",
            "primary_metric", "decision_threshold", "null_model",
            "data_version", "discovery_folia", "test_folia", "inputs")

def validate(root):
    issues = []
    try:
        p = json.loads((root / "protocol.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"protocol": ["cannot read protocol.json: " + str(exc)], "data_split": [], "integrity": []}
    for key in REQUIRED:
        if key not in p or p[key] is None or p[key] == "" or p[key] == []:
            issues.append("missing " + key)
    if not isinstance(p.get("falsifiable_prediction"), str) or not p.get("falsifiable_prediction", "").strip():
        if "missing falsifiable_prediction" not in issues:
            issues.append("invalid falsifiable_prediction")
    split = []
    d, t = p.get("discovery_folia"), p.get("test_folia")
    if not isinstance(d, list) or not isinstance(t, list) or not all(isinstance(x, str) and x for x in d+t):
        split.append("discovery_folia and test_folia must be nonempty lists of folio IDs")
    elif len(d) != len(set(d)) or len(t) != len(set(t)):
        split.append("duplicate folio within partition")
    else:
        for folio in sorted(set(d) & set(t)):
            split.append("folio " + folio + " appears in both discovery and test")
    integrity = []
    inputs = p.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        integrity.append("inputs must contain local file hashes")
    else:
        for item in inputs:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("sha256"), str):
                integrity.append("invalid input descriptor")
                continue
            rel = pathlib.PurePosixPath(item["path"])
            if rel.is_absolute() or ".." in rel.parts or not rel.parts:
                integrity.append("unsafe input path")
                continue
            target = (root / str(rel)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                integrity.append("missing or unsafe input: " + str(rel))
                continue
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest != item["sha256"].lower():
                integrity.append("SHA-256 mismatch: " + str(rel))
    return {"protocol": issues, "data_split": split, "integrity": integrity}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fixtures", type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args()
    expected = {"valid_experiment": True, "incomplete_protocol": False, "overlapping_split": False}
    report = {"cases": [], "passed": True}
    for name, should_accept in expected.items():
        issues = validate(args.fixtures / name)
        accepted = not any(issues.values())
        correct = accepted == should_accept
        report["cases"].append({"fixture": name, "expected": "ACCEPTED" if should_accept else "REJECTED",
                                "actual": "ACCEPTED" if accepted else "REJECTED", "checks": issues, "passed": correct})
        report["passed"] &= correct
        print(("[PASS] " if correct else "[FAIL] ") + name + ": " + ("ACCEPTED" if accepted else "REJECTED"), flush=True)
        for gate, errors in issues.items():
            print("  " + gate + ": " + ("FAIL: " + "; ".join(errors) if errors else "OK"), flush=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
