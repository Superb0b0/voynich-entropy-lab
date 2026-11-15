"""Inventory of permitted page headers, invoked only after trusted filtering.

Never open raw corpora or the holdout policy here.
"""
import hashlib
import json
import pathlib
import re

PAGE = re.compile(rb'^<(f\d+[rv]\d*)>\s+<!', re.M)

def attest(filtered_dir, protected_pages, source_names, output_path):
    root = pathlib.Path(filtered_dir)
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("filtered directory invalid")
    if not protected_pages:
        raise RuntimeError("protection policy empty")
    files = sorted(root.glob("*.txt"))
    if {p.name for p in files} != set(source_names):
        raise RuntimeError("filtered input set mismatch")
    allowed = None
    digests = {}
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("unsafe input")
        raw = path.read_bytes()
        pages = {m.decode("ascii") for m in PAGE.findall(raw)}
        if not pages:
            raise RuntimeError("missing page headers")
        if pages & protected_pages:
            raise RuntimeError("protected content remains in filtered input")
        if allowed is not None and pages != allowed:
            raise RuntimeError('filtered page coverage mismatch')
        allowed = pages
        digests[path.name] = hashlib.sha256(raw).hexdigest()
    if not allowed:
        raise RuntimeError("no common allowed pages")
    output = {
        "schema": "voynich-safe-inventory-v1",
        "status": "FILTERED_ATTESTED_IN_PROCESS",
        "eligible_page_ids": sorted(allowed),
        "filtered_sha256": digests,
        "attestation": "Compared with protected page IDs inside verifier; protected IDs omitted.",
    }
    out = pathlib.Path(output_path)
    if out.exists():
        raise RuntimeError("refuse overwrite")
    out.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    return len(allowed)
