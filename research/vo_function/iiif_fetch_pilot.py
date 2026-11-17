#!/usr/bin/env python3
"""Fetch ten preregistered BL IIIF thumbnails; no image interpretation."""
import argparse, csv, hashlib, json, urllib.request
from pathlib import Path
SELECTED = {9:"f. 1r",10:"f. 1v",11:"f. 2r",12:"f. 2v",13:"f. 3r",222:"f. 106v",223:"f. 107r",224:"f. 107v",225:"f. 108r",226:"f. 108v"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",required=True);p.add_argument("--out",required=True)
    a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    with open(a.inventory,encoding="utf-8",newline="") as f:
        rows={int(r["index"]):r for r in csv.DictReader(f)}
    report=[]
    for idx,label in SELECTED.items():
        r=rows[idx]; record={"index":idx,"expected_label":label,"observed_label":r["canvas_label_unverified"],"source_url":r["image_resource_url"]}
        if record["observed_label"] != label:
            record["status"]="LABEL_MISMATCH";report.append(record);continue
        try:
            req=urllib.request.Request(record["source_url"],headers={"User-Agent":"Voynich-Function-Documentary-Audit/0.1"})
            with urllib.request.urlopen(req,timeout=25) as resp:
                data=resp.read(2_000_001)
                mime=resp.headers.get("Content-Type","")
            if len(data)>2_000_000 or not data.startswith(b"\xff\xd8"):
                raise ValueError("Invalid or oversized JPEG")
            filename=f"canvas_{idx:03d}.jpg";(out/filename).write_bytes(data)
            record.update(status="DOWNLOADED_NOT_ANNOTATED",file=filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=mime)
        except Exception as e:
            record.update(status="FETCH_FAILED",error_type=type(e).__name__,error=str(e)[:300])
        report.append(record)
    (out/"image_fetch_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"selected":len(report),"downloaded":sum(x["status"]=="DOWNLOADED_NOT_ANNOTATED" for x in report),"images_annotated":0}))
if __name__=="__main__":main()
