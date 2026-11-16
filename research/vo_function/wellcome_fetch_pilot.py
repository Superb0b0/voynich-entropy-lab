#!/usr/bin/env python3
"""Acquire deterministic Wellcome MS22 preview sample; no visual coding."""
import csv,hashlib,json,urllib.request
from pathlib import Path
src=Path("wellcome-audit-output/canvas_inventory.csv");out=Path("wellcome-audit-output");out.mkdir(exist_ok=True)
with src.open(newline="",encoding="utf-8") as f:rows=list(csv.DictReader(f))
selected=list(range(1,6))+list(range(len(rows)-4,len(rows)+1))
report=[]
for i in selected:
    row=rows[i-1];url=row["image_resource_url"];entry={"index":i,"label_unverified":row["canvas_label_unverified"],"source_url":url}
    try:
        if not url.startswith("https://iiif.wellcomecollection.org/image/"):raise ValueError("Unexpected image origin")
        req=urllib.request.Request(url,headers={"User-Agent":"VOY-FUNCTION-01-documentary-audit/0.1"})
        with urllib.request.urlopen(req,timeout=30) as r:
            data=r.read(2_000_001);ctype=r.headers.get("Content-Type","")
        if len(data)>2_000_000 or not data.startswith(bytes.fromhex("ffd8")):raise ValueError("Oversize/non-JPEG")
        name=f"wellcome_{i:03}.jpg";(out/name).write_bytes(data)
        entry.update(status="DOWNLOADED_NOT_ANNOTATED",filename=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=ctype)
    except Exception as exc:entry.update(status="FETCH_FAILED",error_type=type(exc).__name__,error=str(exc)[:240])
    report.append(entry)
(out/"image_fetch_report.json").write_text(json.dumps({"selection":"first_five_last_five_canvases_not_representative", "total_canvases":len(rows),"records":report},indent=2)+"\n")
print(json.dumps({"selected":len(report),"downloaded":sum(x["status"]=="DOWNLOADED_NOT_ANNOTATED" for x in report),"images_annotated":0}))
