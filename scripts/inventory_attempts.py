#!/usr/bin/env python3
"""Deterministic read-only attempt inventory; fail closed on unknown/active-incomplete."""
import argparse
import json
import pathlib
import re
import sys

PATTERN = re.compile(r"^[0-9]{3}-[^/]+$")
STATES = {"active", "legacy", "quarantined"}
def inventory(root, registry):
    rows = []
    problems = []
    entries = registry.get("attempts", {})
    if not isinstance(entries, dict):
        return [], ["registry attempts must be a mapping"]
    present = sorted(p for p in root.iterdir() if p.is_dir() and PATTERN.fullmatch(p.name)) if root.is_dir() else []
    for folder in present:
        name = folder.name
        entry = entries.get(name)
        has_config = (folder / "attempt.yml").is_file()
        state = entry.get("state") if isinstance(entry, dict) else "unknown"
        reason = entry.get("reason") if isinstance(entry, dict) else None
        if state not in STATES:
            problems.append(name + ": unknown or invalid state")
        if state in {"legacy", "quarantined"}:
            if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("reason", "evidence", "classified_on", "decision_commit", "decision_owner")):
                problems.append(name + ": incomplete classification record")
            if entry.get("eligible_for_evidence_promotion") is not False:
                problems.append(name + ": legacy/quarantine must prohibit evidence promotion")
        if state == "active" and not has_config:
            problems.append(name + ": active attempt missing attempt.yml")
        rows.append({"attempt_id": name, "state": state, "attempt_yml": "present" if has_config else "missing",
                     "evidence_eligible": state == "active" and has_config, "reason": reason})
    for name in sorted(set(entries) - {p.name for p in present}):
        problems.append(name + ": registry entry absent from disk")
    if not present:
        problems.append("no attempt directories found")
    return rows, problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("attempts", type=pathlib.Path)
    ap.add_argument("registry", type=pathlib.Path)
    ap.add_argument("--report", type=pathlib.Path, required=True)
    args = ap.parse_args()
    try:
        config = json.loads(args.registry.read_text(encoding="utf-8"))
        rows, errors = inventory(args.attempts, config)
    except (OSError, ValueError, TypeError) as exc:
        rows, errors = [], ["inventory read error: " + str(exc)]
    report = {"attempts": rows, "errors": errors, "passed": not errors,
              "note": "Inventory is not replay verification or scientific validation."}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print("[INVENTORY] {attempt_id}: {state}, attempt.yml={attempt_yml}".format(**row))
    for error in errors:
        print("[FAIL] " + error, file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
