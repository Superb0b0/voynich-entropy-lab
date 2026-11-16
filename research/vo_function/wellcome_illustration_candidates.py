#!/usr/bin/env python3
"""Fetch visually flagged Wellcome MS.22 IIIF folios at full service size.

The official catalogue states that the manuscript contains 12 apparatus drawings,
but does not give their folio locations. This script therefore preserves the
visual sweep as candidate pages; it never asserts a one-to-one mapping or labels
objects semantically.
"""
import csv, hashlib, json, urllib.request
from pathlib import Path

ROOT = Path("wellcome-audit-output")
# Candidate canvases flagged by a full 228-preview contact-sheet sweep.
# The list deliberately includes ambiguous/vessel-only sketches; see status field.
CANDIDATES = [146, 148, 154, 156, 160, 161, 163, 164, 167, 177, 179, 186, 192, 210, 212, 213]

def main():
    with (ROOT / "canvas_inventory.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    report = []
    target = ROOT / "apparatus_candidates"
    target.mkdir(parents=True, exist_ok=True)
    for i in CANDIDATES:
        row = rows[i - 1]
        url = row["image_resource_url"].replace("/full/756,1024/", "/full/full/")
        label = row["canvas_label_unverified"]
        item = {
            "canvas_index": i,
            "manifest_label": label or "UNLABELED",
            "folio_mapping": "IIIF label only; not independently verified",
            "canvas_id": row["canvas_id"],
            "source_url": url,
            "selection_status": "VISUAL_CANDIDATE_NOT_INSTITUTIONALLY_ITEMIZED",
        }
        try:
            if not url.startswith("https://iiif.wellcomecollection.org/image/"):
                raise ValueError("Unexpected image service")
            req = urllib.request.Request(url, headers={"User-Agent":"VOY-FUNCTION-01-documentary-audit/0.2"})
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read(10_000_001)
                mime = response.headers.get("Content-Type", "")
            if len(data) > 10_000_000 or not data.startswith(bytes.fromhex("ffd8")):
                raise ValueError("Oversized or invalid JPEG")
            filename = f"canvas_{i:03d}.jpg"
            path = target / filename
            path.write_bytes(data)
            from PIL import Image
            dimensions = Image.open(path).size
            item.update(status="DOWNLOADED", filename=f"apparatus_candidates/{filename}",
                        bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                        dimensions=list(dimensions), content_type=mime)
        except Exception as exc:
            item.update(status="FETCH_FAILED", error_type=type(exc).__name__, error=str(exc)[:300])
        report.append(item)
    (ROOT / "apparatus_candidate_fetch_report.json").write_text(
        json.dumps({
            "catalogue_statement": "12 carefully executed pen-drawings of alchemical apparatus",
            "catalogue_source": "https://wellcomecollection.org/works/ugn23v6p",
            "manifest_url": "https://iiif.wellcomecollection.org/presentation/v2/b19480271",
            "manifest_sha256": "1672e82e656b7ff66cf678d4c69f509fc35b9df7d04cb6bd5f705d96487fcf7c",
            "selection_method": "visual contact-sheet sweep of all 228 manifest canvases",
            "institutional_folio_locator": "not supplied by catalogue; IIIF labels retained verbatim",
            "candidate_pages_are_not_claimed_to_be_a_complete_or_one_to_one_list": True,
            "records": report
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"selected":len(report),
                      "downloaded":sum(x.get("status")=="DOWNLOADED" for x in report),
                      "failed":sum(x.get("status")!="DOWNLOADED" for x in report)}))

if __name__ == "__main__":
    main()
