#!/usr/bin/env python3
"""Wellcome MS.22 IIIF inventory: catalogue-derived URL, no image interpretation."""
import csv,hashlib,json,urllib.request,datetime
from pathlib import Path
ROOT=Path("wellcome-audit-output");ROOT.mkdir(exist_ok=True)
URL="https://api.wellcomecollection.org/catalogue/v2/works/akn92u5z?include=items"
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"VOY-FUNCTION-01-documentary-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=35) as resp:return resp.read()
audit={"work":"akn92u5z","checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"images_inspected":0,"annotations_executed":0}
try:
    data=fetch(URL);work=json.loads(data);audit["catalogue_sha256"]=hashlib.sha256(data).hexdigest()
    candidates=[loc["url"] for item in work.get("items",[]) for loc in item.get("locations",[]) if loc.get("locationType",{}).get("id")=="iiif-presentation" and loc.get("url","").startswith("https://")]
    audit["candidate_manifest_urls"]=candidates
    if not candidates:raise ValueError("No catalogue-derived iiif-presentation URL")
    url=candidates[0];raw=fetch(url);m=json.loads(raw)
    audit.update(status="MANIFEST_PARSED",manifest_url=url,manifest_sha256=hashlib.sha256(raw).hexdigest())
    canvases=m.get("sequences",[{}])[0].get("canvases",[]) if "sequences" in m else m.get("items",[])
    audit["canvas_count"]=len(canvases)
    with open(ROOT/"canvas_inventory.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["index","canvas_id","canvas_label_unverified","image_resource_url"])
        for i,c in enumerate(canvases,1):
            label=c.get("label","")
            if isinstance(label,dict):label=" / ".join(str(v) for vals in label.values() for v in (vals if isinstance(vals,list) else [vals]))
            img=(c.get("images",[{}])[0].get("resource",{}).get("@id","") if "images" in c else c.get("items",[{}])[0].get("items",[{}])[0].get("body",{}).get("id",""))
            w.writerow([i,c.get("@id",c.get("id","")),label,img])
except Exception as e:audit.update(status="ACCESS_FAILED",error_type=type(e).__name__,error=str(e)[:300])
(ROOT/"audit.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(audit))
