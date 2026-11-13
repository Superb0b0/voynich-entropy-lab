#!/usr/bin/env python3
"""Fail-closed CI verifier. Uses Linux strace to audit attempt file reads."""
import hashlib, json, os, pathlib, re, shlex, shutil, subprocess, sys, tempfile
import yaml

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"MANIFEST.md"
HOLDOUT=ROOT/"HOLDOUT.md"
NUM=re.compile(r"^[0-9a-f]{64}$")
ATTEMPT=re.compile(r"^[0-9]{3}-[^/]+$")

def fail(msg):
    raise RuntimeError(msg)

def hashes():
    manifest=MANIFEST.read_text()
    expected={}
    for line in manifest.splitlines():
        if not line.startswith("|"):continue
        cells=[c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells)>=3 and re.fullmatch(r"data/[^/]+\.txt",cells[0]) and NUM.fullmatch(cells[2]):
            expected[cells[0]]=cells[2]
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT/"data").glob("*.txt")}
    if not actual or set(actual)!=set(expected):fail(f"MANIFEST file set mismatch: actual={sorted(actual)} expected={sorted(expected)}")
    for name,digest in actual.items():
        if digest!=expected[name]:fail(f"SHA256 mismatch: {name}")
    return actual

def protected():
    text=HOLDOUT.read_text()
    # HOLDOUT currently defines protected folio/page IDs, not independent files.
    pages=set(re.findall(r"['\"](f\d+[rv]\d*)['\"]",text))
    if not pages:fail("HOLDOUT.md lacks machine-readable protected page IDs")
    return pages

def sanitize(data, pages):
    # Input is IVTFF; exclude entire protected page blocks, not just their P-lines.
    page_re=re.compile(r"^<(f\d+[rv]\d*)>\s+<!")
    out=[];skip=False
    for line in data.splitlines(keepends=True):
        m=page_re.match(line)
        if m:skip=m.group(1) in pages
        if not skip:out.append(line)
    return "".join(out)

def compare(a,b,tol,path="$"):
    if isinstance(a,bool) or isinstance(b,bool):
        if a!=b:fail(f"{path}: boolean mismatch")
    elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
        import math
        if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>tol:
            fail(f"{path}: {a} vs {b}, tolerance={tol}")
    elif isinstance(a,dict) and isinstance(b,dict):
        if set(a)!=set(b):fail(f"{path}: keys differ")
        for k in a:compare(a[k],b[k],tol,path+"."+str(k))
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):fail(f"{path}: lengths differ")
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,tol,f"{path}[{i}]")
    elif a!=b:fail(f"{path}: mismatch")

def verify_attempt(folder, safe_dir, forbidden):
    cfg_path=folder/"attempt.yml"
    if not cfg_path.is_file():fail(f"{folder.name}: missing attempt.yml; cannot infer execution contract")
    cfg=yaml.safe_load(cfg_path.read_text())
    if not isinstance(cfg,dict):fail(f"{folder.name}: invalid attempt.yml")
    seed=cfg.get("seed")
    if not isinstance(seed,int) or isinstance(seed,bool):fail(f"{folder.name}: explicit integer seed required")
    tol=cfg.get("tolerance")
    if not isinstance(tol,(int,float)) or isinstance(tol,bool) or tol<0:fail(f"{folder.name}: nonnegative numeric tolerance required")
    cmd=cfg.get("command")
    if cmd is None:
        if not (folder/"run.sh").is_file():fail(f"{folder.name}: missing run.sh and command")
        cmd=["bash","run.sh"]
    elif isinstance(cmd,str):cmd=shlex.split(cmd)
    if not isinstance(cmd,list) or not cmd or not all(isinstance(x,str) and x for x in cmd):
        fail(f"{folder.name}: command must be a nonempty string or argv list")
    expected=folder/"results.json"
    if not expected.is_file():fail(f"{folder.name}: missing committed results.json")
    output=folder/"results_ci.json"
    output.unlink(missing_ok=True)
    env=os.environ.copy()
    env.update({"PYTHONHASHSEED":str(seed),"VOYNICH_SEED":str(seed),
                "VOYNICH_DATA_DIR":str(safe_dir),"VOYNICH_HOLDOUT_POLICY":"TRAIN_ONLY"})
    with tempfile.TemporaryDirectory() as td:
        trace=pathlib.Path(td)/"trace"
        run=subprocess.run(["strace","-f","-qq","-e","trace=open,openat,openat2,readlink,readlinkat",
                            "-s","4096","-o",str(trace),"--",*cmd],cwd=folder,env=env,
                           timeout=600,capture_output=True,text=True)
        log=trace.read_text(errors="replace")
        # Fail closed on any attempt to access the original corpus or HOLDOUT.md.
        # strace paths can be relative to cwd or absolute.
        for raw in re.findall(r'(?:open|openat|openat2|readlink|readlinkat)\([^\n]*?"([^"\n]+)"',log):
            candidate=(folder/raw).resolve() if not os.path.isabs(raw) else pathlib.Path(raw).resolve()
            if candidate in forbidden or candidate==HOLDOUT.resolve():
                fail(f"{folder.name}: protected input access: {candidate}")
        if run.returncode:fail(f"{folder.name}: command failed ({run.returncode}): {run.stderr[-1200:]}")
    if not output.is_file():fail(f"{folder.name}: no results_ci.json produced")
    compare(json.loads(expected.read_text()),json.loads(output.read_text()),tol)

def main():
    hashes()
    pages=protected()
    if shutil.which("strace") is None:fail("strace unavailable; cannot audit reads")
    attempts=sorted(p for p in (ROOT/"attempts").glob("*") if p.is_dir() and ATTEMPT.fullmatch(p.name))
    if not attempts:fail("No attempts/NNN-*/ found; verification is NOT VERIFIED")
    forbidden={p.resolve() for p in (ROOT/"data").glob("*.txt")}
    with tempfile.TemporaryDirectory() as td:
        safe_dir=pathlib.Path(td)/"data";safe_dir.mkdir()
        for source in (ROOT/"data").glob("*.txt"):
            # IVTFF folio filtering only applies to identified page-structured corpora.
            raw=source.read_text()
            if not re.search(r"^<f\d+[rv]\d*>\s+<!",raw,re.M):
                fail(f"{source.name}: cannot safely remove holdout pages")
            (safe_dir/source.name).write_text(sanitize(raw,pages))
        for folder in attempts:verify_attempt(folder,safe_dir,forbidden)
    print(f"VERIFIED: {len(attempts)} attempts, SHA256 manifest, traced holdout isolation")

if __name__=="__main__":
    try:main()
    except (RuntimeError,subprocess.TimeoutExpired,ValueError,KeyError) as exc:
        print(f"NON VERIFICATO: {exc}",file=sys.stderr)
        sys.exit(1)
