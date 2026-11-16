"""Read-only structural reconciliation of two independently supplied manifests.

This does NOT parse or access Voynich data. It compares supplied JSON manifest
records and emits differences. A PASS on synthetic fixtures is NOT parser parity
attestation; an independent reviewer must verify the manifest provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path


def compare(reference, candidate):
    """Compare blocks and loci by stable IDs, including exact structural fields."""
    differences = []
    for kind, fields in (
        ("blocks", ("page", "start", "end", "order")),
        ("loci", ("page", "block_id", "physical_index", "tokens", "next_locus_id")),
    ):
        left, right = reference.get(kind), candidate.get(kind)
        if not isinstance(left, list) or not isinstance(right, list):
            differences.append({"kind": kind, "error": "missing_or_invalid_array"})
            continue
        def index(records, side):
            indexed = {}
            for row in records:
                if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                    differences.append({"kind": kind, "side": side, "error": "invalid_record"})
                    continue
                if row["id"] in indexed:
                    differences.append({"kind": kind, "side": side, "id": row["id"], "error": "duplicate_id"})
                indexed[row["id"]] = row
            return indexed
        a, b = index(left, "reference"), index(right, "candidate")
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                differences.append({"kind": kind, "id": key, "error": "missing_id",
                                    "side": "reference" if key not in a else "candidate"})
                continue
            for field in fields:
                if field not in a[key] or field not in b[key] or a[key][field] != b[key][field]:
                    differences.append({"kind": kind, "id": key, "field": field,
                                        "error": "field_mismatch"})
    return {"status": "MATCH" if not differences else "DIFFERENCES",
            "differences": differences,
            "reference_counts": {k: len(reference.get(k, [])) for k in ("blocks", "loci")},
            "candidate_counts": {k: len(candidate.get(k, [])) for k in ("blocks", "loci")}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reference", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    raw_a, raw_b = args.reference.read_bytes(), args.candidate.read_bytes()
    result = compare(json.loads(raw_a), json.loads(raw_b))
    result["reference_sha256"] = hashlib.sha256(raw_a).hexdigest()
    result["candidate_sha256"] = hashlib.sha256(raw_b).hexdigest()
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(serialized + "\n")
    else:
        print(serialized)
    return 0 if result["status"] == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
