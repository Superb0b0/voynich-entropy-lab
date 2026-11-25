import csv, hashlib, io, json, zipfile
from pathlib import Path
p=Path("cal01-input/work/VOY-REFLOW-CAL-01/output/ZL3b_04")
orig=Path("experiments/cal01-diagnostic/evidence/diagnostic-ZL3b_04-a1.zip")
sha=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(orig) as z:
    failed={n:z.read(n) for n in ("H1.json","stream.sha256","reflow.csv")}
with zipfile.ZipFile("cal01-input/VOY-REFLOW-CAL-01_CHECKPOINT.zip") as z:
    local={n:z.read("VOY-REFLOW-CAL-01/output/ZL3b_04/"+n) for n in failed}
repeat={n:(p/n).read_bytes() for n in failed}
l,f,r=(json.loads(x["H1.json"]) for x in (local,failed,repeat))
csvrows=lambda b:list(csv.DictReader(io.StringIO(b.decode())))
result={"scope":"diagnostic only; not a qualifying scientific shard","strict_exit_code":int(Path("diagnosis/exit-code.txt").read_text()),"local_H1":l,"failed_H1":f,"repeat_H1":r,"H1_exact_vs_local":repeat["H1.json"]==local["H1.json"],"H1_exact_vs_failed":repeat["H1.json"]==failed["H1.json"],"stream_exact_vs_both":local["stream.sha256"]==repeat["stream.sha256"]==failed["stream.sha256"],"original_prefix_exact":repeat["reflow.csv"].startswith(local["reflow.csv"]),"rows":len(csvrows(repeat["reflow.csv"])),"CSV_exact_vs_failed":repeat["reflow.csv"]==failed["reflow.csv"],"hashes":{label:{n:sha(b) for n,b in d.items()} for label,d in (("local",local),("failed",failed),("repeat",repeat))}}
Path("diagnosis/comparison.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
if result["rows"]!=1000 or not result["original_prefix_exact"] or not result["stream_exact_vs_both"]:
    raise RuntimeError("incomplete or inconsistent diagnostic; no retry")
