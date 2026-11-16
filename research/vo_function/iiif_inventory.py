#!/usr/bin/env python3
"""Read-only IIIF manifest inventory. No Voynich corpus or image annotation."""
import argparse
import csv
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DEFAULT = "https://bl.digirati.io/iiif/ark:/81055/vdc_100165172997.0x000001"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Voynich-Function-Documentary-Audit/0.1", "Accept": "application/json, application/ld+json"})
    with urllib.request.urlopen(req, timeout=35) as resp:
        raw = resp.read(30_000_001)
        if len(raw) > 30_000_000:
            raise ValueError("Manifest too large (>30 MB)")
        return json.loads(raw), hashlib.sha256(raw).hexdigest()

def inventory(m):
    if "items" in m:  # IIIF Presentation v3
        for i, c in enumerate(m.get("items", []), 1):
            anns = c.get("items", [])
            urls = []
            for page in anns:
                for ann in page.get("items", []):
                    body = ann.get("body", {})
                    bodies = body if isinstance(body, list) else [body]
                    urls.extend(b.get("id", "") for b in bodies if isinstance(b, dict) and b.get("id"))
            label = c.get("label", {})
            if isinstance(label, dict):
                label = " | ".join(str(v) for vals in label.values() for v in (vals if isinstance(vals, list) else [vals]))
            yield i, c.get("id", ""), str(label), " | ".join(urls), c.get("width", ""), c.get("height", "")
    elif "sequences" in m:  # IIIF Presentation v2
        for i, c in enumerate(m.get("sequences", [{}])[0].get("canvases", []), 1):
            urls = []
            for ann in c.get("images", []):
                resource = ann.get("resource", {})
                if isinstance(resource, dict):
                    urls.append(resource.get("@id", ""))
            yield i, c.get("@id", ""), str(c.get("label", "")), " | ".join(urls), c.get("width", ""), c.get("height", "")
    else:
        raise ValueError("Unrecognized IIIF Presentation v2/v3 manifest")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", default=DEFAULT)
    p.add_argument("--out", default="iiif-audit-output")
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    try:
        m, sha = get_json(a.manifest)
        rows = list(inventory(m))
        with (out / "canvas_inventory.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["index", "canvas_id", "canvas_label_unverified", "image_resource_url", "width", "height", "folio_verified", "annotation_status"])
            for row in rows:
                w.writerow([*row, "NO", "NOT_EXECUTED"])
        result = {"status":"MANIFEST_PARSED", "source_url":a.manifest, "checked_at_utc":stamp, "manifest_sha256":sha, "canvas_count":len(rows), "folio_mapping_verified":False, "images_inspected":0, "annotations_executed":0}
    except Exception as exc:
        result = {"status":"ACCESS_FAILED", "source_url":a.manifest, "checked_at_utc":stamp, "error_type":type(exc).__name__, "error":str(exc)[:500], "images_inspected":0, "annotations_executed":0}
    (out / "audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "MANIFEST_PARSED" else 2

if __name__ == "__main__":
    sys.exit(main())
