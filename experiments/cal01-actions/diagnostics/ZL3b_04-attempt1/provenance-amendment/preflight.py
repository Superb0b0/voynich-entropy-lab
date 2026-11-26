"""Verifica di provenienza su tre archivi originali. Solo libreria standard."""
import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

FROZEN = "0fb8b0ddb2ab1281758834e501f166669646518e"
CHECKPOINT = "6043b1935029ba0e5b53e0cd9f65d0b70601b1d998e605840fa32cb805541a4d"
FIELDS = "geometry realization reflow_id seed n_transitions gain_nats status error".split()
CASES = (
    (15018135784, "761292fa3157b379632f2097ed44cb524af507dd4760db305138a829f3862c33", 0, 4, range(212,262)),
    (15017881677, "91eb3dfc4d118cb2c4806d44f04c0ea5b5085636969558814fcece81206b150b", 0, 9, range(901,911)),
    (15018760069, "7f1758dcc88500484e4e5072419143e6d579ee9aeb49a91169f24107d4462002", 1, 1, range(901,911)),
)
FAILED_FILES = {
    "reflow.csv":"f61531511301a7adc0000a849ce1a0866ed73b3eb41bf5354e5962af8864cc97",
    "H1.json":"1cb601b446a704ae51938f6f8e4a6f911e669d9e12a7f6bb7c71e853ef0b641d",
    "stream.sha256":"933acb1bd16f81b34f1342d105503042158911f1ae168c9f0943877253b191ae",
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def inspect_rows(raw, g, r, selected):
    lines = raw.splitlines(keepends=True)
    require(len(lines)==1001 and all(line.endswith(b'\r\n') for line in lines), "CSV framing")
    reader = csv.DictReader(io.StringIO(raw.decode("ascii"),newline=""))
    require(reader.fieldnames==FIELDS, "CSV header")
    series = ("ZL3b","IT2a")[g]
    proof = []
    for i,(row,line) in enumerate(zip(reader,lines[1:],strict=True),1):
        seed = f"20261124:502:{g}:{r}:{i}"
        require(None not in row and None not in row.values(), "CSV width")
        require((row["geometry"],row["realization"],row["reflow_id"],row["seed"]) ==
                (series,str(r),str(i),seed), "ID or seed")
        require(row["status"]=="OK" and row["error"]=="" and
                row["n_transitions"]==str((2977,2936)[g]), "technical fields")
        if i in selected:
            proof.append(dict(id=i,seed=seed,row_sha256=sha(line)))
    require([p["id"] for p in proof]==list(selected), "panel incomplete")
    return proof

def verify(folder):
    result = []
    for aid,expected,g,r,ids in CASES:
        raw = (folder/f"{aid}.zip").read_bytes()
        require(sha(raw)==expected, f"archive digest {aid}")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = z.namelist()
            if aid==15018135784:
                expected_members = FAILED_FILES
                proof_type = "pinned_failed_archive"
            else:
                manifest = json.loads(z.read("manifest.json"))
                require(manifest["frozen_commit"]==FROZEN and manifest["archive_sha256"]==CHECKPOINT
                        and (manifest["g"],manifest["r"],manifest["rows"])==(g,r,1000)
                        and manifest["complete"] is True, "original shard manifest")
                expected_members = manifest["files"]
                proof_type = "original_shard_manifest"
            inventory = set(expected_members)
            if proof_type=="original_shard_manifest":
                inventory.add("manifest.json")
            require(len(names)==len(inventory) and set(names)==inventory, "ZIP inventory")
            require(all(sha(z.read(k))==v for k,v in expected_members.items()), "member digest")
            rows = inspect_rows(z.read("reflow.csv"),g,r,ids)
            result.append(dict(artifact_id=aid,archive_sha256=expected,proof_type=proof_type,
                               member_sha256=expected_members,rows=rows))
    return dict(original_run=45605270057,source_commit=FROZEN,shards=result)

if __name__=="__main__":
    folder = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/"originals"
    print(json.dumps(verify(folder),indent=2))
