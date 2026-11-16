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
    if not isinstance(reference, dict) or not isinstance(candidate, dict):
        return {"status": "DIFFERENCES",
                "differences": [{"kind": "manifest", "error": "invalid_top_level_object"}],
                "reference_counts": {"blocks": 0, "loci": 0},
                "candidate_counts": {"blocks": 0, "loci": 0}}
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
        for side, indexed in (("reference", a), ("candidate", b)):
            for record_id, record in indexed.items():
                for field in fields:
                    if field not in record:
                        differences.append({"kind": kind, "side": side, "id": record_id,
                                            "field": field, "error": "missing_required_field"})
                if kind == "loci" and "tokens" in record and (
                        not isinstance(record["tokens"], list)
                        or any(not isinstance(token, str) for token in record["tokens"])):
                    differences.append({"kind": kind, "side": side, "id": record_id,
                                        "error": "invalid_token_stream"})
                if kind == "loci" and "physical_index" in record and (
                        type(record["physical_index"]) is not int
                        or record["physical_index"] < 1):
                    differences.append({"kind": kind, "side": side, "id": record_id,
                                        "error": "invalid_physical_index"})
                if kind == "loci" and "next_locus_id" in record and (
                        record["next_locus_id"] is not None
                        and not isinstance(record["next_locus_id"], str)):
                    differences.append({"kind": kind, "side": side, "id": record_id,
                                        "field": "next_locus_id", "error": "invalid_next_locus_id"})
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                differences.append({"kind": kind, "id": key, "error": "missing_id",
                                    "side": "reference" if key not in a else "candidate"})
                continue
            for field in fields:
                if field not in a[key] or field not in b[key] or a[key][field] != b[key][field]:
                    differences.append({"kind": kind, "id": key, "field": field,
                                        "error": "field_mismatch"})
    # A field-by-field match is insufficient if both manifests contain
    # dangling or cross-page block/adjacency references.
    for side, manifest in (("reference", reference), ("candidate", candidate)):
        block_rows = manifest.get("blocks")
        locus_rows = manifest.get("loci")
        if not isinstance(block_rows, list) or not isinstance(locus_rows, list):
            continue
        blocks = {row.get("id"): row for row in block_rows
                  if isinstance(row, dict) and isinstance(row.get("id"), str)}
        loci = {row.get("id"): row for row in locus_rows
                if isinstance(row, dict) and isinstance(row.get("id"), str)}
        for locus_id, locus in loci.items():
            block = blocks.get(locus.get("block_id"))
            if block is None:
                differences.append({"kind": "loci", "side": side, "id": locus_id,
                                    "field": "block_id", "error": "unknown_block_reference"})
            elif locus.get("page") != block.get("page"):
                differences.append({"kind": "loci", "side": side, "id": locus_id,
                                    "field": "page", "error": "block_page_mismatch"})
            next_id = locus.get("next_locus_id")
            if isinstance(next_id, str):
                successor = loci.get(next_id)
                if successor is None:
                    differences.append({"kind": "loci", "side": side, "id": locus_id,
                                        "field": "next_locus_id", "error": "unknown_locus_reference"})
                elif (locus.get("block_id") != successor.get("block_id")
                      or locus.get("page") != successor.get("page")
                      or type(locus.get("physical_index")) is not int
                      or type(successor.get("physical_index")) is not int
                      or successor["physical_index"] != locus["physical_index"] + 1):
                    differences.append({"kind": "loci", "side": side, "id": locus_id,
                                        "field": "next_locus_id", "error": "invalid_adjacency_reference"})
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
