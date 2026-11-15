#!/usr/bin/env python3
"""TRAIN_ONLY-only diagnostic; never reads Git metadata or original corpus.
Run in a directory with NO .git; requires VOYNICH_DATA_DIR pointing to a
pre-filtered IVTFF corpus and explicit --expected-sha256 of that filtered file.
Produces descriptive conditional-permutation null, NOT a scientific verdict.
"""
import argparse, collections, hashlib, json, os, pathlib, random, re, sys
CL=("qo","ch","sh","d","o","y","s")
def die(s): raise SystemExit("FAIL_CLOSED: "+s)
def parse(raw):
    rows=collections.defaultdict(list); page=None; leaf=None; para=0
    for line in raw.splitlines():
        m=re.match(r"^<(f\d+[rv]\d*)>",line)
        if m: page=m[1]; leaf=int(re.match(r"f(\d+)",page)[1]); para=0; continue
        m=re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)",line)
        if not m or m[1]!=page: continue
        n,loc,s=int(m[2]),m[3],m[4]
        if "P" not in loc: continue
        if "*P" in loc or "@P" in loc: para+=1
        s=re.sub(r"<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]","",s)
        tok=[re.sub(r"[^a-z]","",t.lower()) for t in re.split(r"[.,\s]+",s.strip())]
        tok=[t for t in tok if t]
        if tok: rows[(leaf,page,para)].append((n,tok[0]))
    return rows
def cls(w): return next((i for i,p in enumerate(CL) if w.startswith(p)),7)
def stat(groups, rng=None):
    counts=[0,0,0]; pairs=0
    for w,valid in groups:
        a=list(w)
        if rng is not None: rng.shuffle(a)
        for i,v in enumerate(valid):
            if not v:continue
            pairs+=1; x,y=a[i],a[i+1];cx,cy=cls(x),cls(y)
            if cx==cy:counts[1 if cx==0 else 0]+=1
            if x==y:counts[2]+=1
    return pairs,counts
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",choices=["ZL3b-n.txt","IT2a-n.txt"],required=True)
    ap.add_argument("--expected-sha256",required=True)
    ap.add_argument("--replicates",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=20261115)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    if a.replicates!=1000 or a.seed!=20261115:die("frozen seed/replicates mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}",a.expected_sha256):die("bad SHA256")
    data=os.environ.get("VOYNICH_DATA_DIR")
    if not data:die("VOYNICH_DATA_DIR missing")
    root=pathlib.Path.cwd()
    if any((p/".git").exists() for p in [root,*root.parents]):die(".git accessible from cwd")
    d=pathlib.Path(data).resolve()
    if not d.is_dir() or ".git" in d.parts:die("unsafe data directory")
    f=d/a.corpus
    if not f.is_file():die("filtered corpus missing")
    raw=f.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.expected_sha256:die("filtered corpus SHA256 mismatch")
    rows=parse(raw.decode("utf-8"))
    groups=[]
    for key in sorted(rows):
        rr=sorted(rows[key]);valid=[rr[i+1][0]==rr[i][0]+1 for i in range(len(rr)-1)]
        if any(valid):groups.append(([w for _,w in rr],valid))
    if not groups:die("no valid training paragraph pairs")
    n,observed=stat(groups)
    rng=random.Random(a.seed)
    sims=[stat(groups,rng)[1] for _ in range(a.replicates)]
    metrics=["same_nonqo","qoqo","repeat"]
    out={"status":"DESCRIPTIVE_ONLY","corpus":a.corpus,"filtered_sha256":a.expected_sha256,"seed":a.seed,"replicates":a.replicates,"paragraph_groups":len(groups),"valid_pairs":n,"metrics":{}}
    for k,m in enumerate(metrics):
        v=sorted(s[k] for s in sims)
        out["metrics"][m]={"observed":observed[k],"null_mean":sum(v)/len(v),"null_95pct":[v[24],v[974]],"null_min":v[0],"null_max":v[-1]}
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
