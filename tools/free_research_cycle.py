#!/usr/bin/env python3
"""Zero-API deterministic exploratory batch. Standard-library only, training leaves only."""
import collections, hashlib, json, random, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
EXPECTED="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
HELD=frozenset({2,5,9,17,31,32,36,37,38,45,48,49,67,69,78,85,86,94,95,101,111})
SEED=20261114
N=1000
OUT=ROOT/"research-output"
def load():
    raw=(ROOT/"data/ZL3b-n.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise SystemExit("BLOCKED: SHA mismatch")
    page=None; leaf=None; para=0
    groups=collections.defaultdict(list)
    for line in raw.decode("utf-8").splitlines():
        m=re.match(r"^<(f\d+[rv]\d*)>\s+<!",line)
        if m:
            page=m[1];leaf=int(re.match(r"f(\d+)",page)[1]);para=0
            continue
        # Do not inspect text from held-out leaves.
        if leaf is None or leaf in HELD:continue
        m=re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)",line)
        if not m or m[1]!=page or "P" not in m[3]:continue
        if "@P" in m[3] or "*P" in m[3]:para+=1
        s=re.sub(r"<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]","",m[4])
        words=[re.sub(r"[^a-z]","",w.lower()) for w in re.split(r"[.,\s]+",s)]
        words=[w for w in words if w]
        if words:groups[(leaf,page,para)].append((int(m[2]),words[0],len(words)))
    return groups
def test(groups,kind,seed):
    rng=random.Random(seed)
    output=[]
    for split in (0,1):
        selected=[sorted(v) for k,v in groups.items() if int(hashlib.sha256((str(k[0])+":"+str(SEED)).encode()).hexdigest(),16)%2==split]
        def metric(shuffle):
            hit=den=0
            for g in selected:
                words=[x[1] for x in g]
                if shuffle:rng.shuffle(words)
                for i in range(len(g)-1):
                    if g[i+1][0]!=g[i][0]+1:continue
                    a,b=words[i],words[i+1]
                    if kind=="same_prefix":
                        den+=1;hit+=a[:2]==b[:2]
                    elif kind=="qo_transition":
                        if a.startswith("qo"):den+=1;hit+=b.startswith("qo")
                    elif kind=="firstword_repeat":
                        den+=1;hit+=a==b
            return hit,den
        obs,den=metric(False)
        null=[metric(True)[0] for _ in range(N)]
        avg=sum(null)/N
        p=(1+sum(x<=obs for x in null))/(N+1)
        output.append({"split":split,"observed":obs,"denominator":den,"null_mean":avg,"observed_over_expected":obs/avg if avg else None,"p_one_sided_depletion":p,"null_95":[sorted(null)[24],sorted(null)[975]]})
    return output
def main():
    groups=load()
    if not groups:raise SystemExit("BLOCKED: no eligible training paragraphs")
    OUT.mkdir(exist_ok=True)
    # All three hypotheses fixed in code before execution, not generated adaptively.
    tests={"firstword_repeat":test(groups,"firstword_repeat",SEED),
           "qo_transition":test(groups,"qo_transition",SEED+1),
           "same_prefix":test(groups,"same_prefix",SEED+2)}
    pvals=[(kind,row["split"],row["p_one_sided_depletion"]) for kind,rows in tests.items() for row in rows]
    ordered=sorted(pvals,key=lambda x:x[2]);m=len(ordered);prev=0
    adjusted={}
    for i,(kind,split,p) in enumerate(ordered):
        prev=max(prev,min(1,p*(m-i)))
        adjusted[(kind,split)]=prev
    for kind,rows in tests.items():
        for row in rows:row["holm_family_6"]=adjusted[(kind,row["split"])]
    result={"status":"EXPLORATORY_NOT_VALIDATED","generated_at":datetime.now(timezone.utc).isoformat(),
            "corpus_sha256":EXPECTED,"seed":SEED,"permutations":N,"unit":"consecutive P lines within training paragraph",
            "null":"within-paragraph first-word shuffle","splits":"SHA256(leaf:20261114) parity",
            "heldout_folios_accessed":False,"groups":len(groups),"tests":tests,
            "warning":"Hypotheses previously investigated; NOT new qualifying attempts, NOT independent validation."}
    (OUT/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    (OUT/"SUMMARY.md").write_text("# Automated exploratory training-only checks\n\n"
      +"Not a decipherment; not new independent hypotheses. Six p-values Holm corrected.\n\n"
      +"| Test | Split | Observed | Rival mean | O/E | p | Holm (6) |\n|---|---:|---:|---:|---:|---:|---:|\n"
      +"".join(f"| {k} | {v['split']} | {v['observed']} | {v['null_mean']:.3f} | {v['observed_over_expected']:.3f} | {v['p_one_sided_depletion']:.4f} | {v['holm_family_6']:.4f} |\n" for k,rows in tests.items() for v in rows))
    print("PASS: three training-only exploratory checks archived as artifacts; zero external calls")
if __name__=="__main__":main()
