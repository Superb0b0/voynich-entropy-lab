#!/usr/bin/env python3
"""Exploratory qo adjacency rival calibration. No paid services; no holdout metrics."""
import collections, hashlib, json, random, re
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/ZL3b-n.txt"
SHA="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
HELD={2,5,9,17,31,32,36,37,38,45,48,49,67,69,78,85,86,94,95,101,111}
SEED=20261113
REPS=2000
PAGE=re.compile(r"^<(f(\d+)[rv]\d*)>\s+<!")
LINE=re.compile(r"^<(f(\d+)[rv]\d*)\.(\d+),([^>]*)>\s*(.*)")
def parse():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise SystemExit("FAIL CLOSED: corpus SHA")
    current=None;groups=collections.defaultdict(list);paragraph=0
    for s in raw.decode("utf-8").splitlines():
        p=PAGE.match(s)
        if p:current=p[1];paragraph=0;continue
        m=LINE.match(s)
        if not m or current is None or int(m[2]) in HELD or m[1]!=current:continue
        locus=m[4]
        if not re.match(r"^[*@+=]P",locus):continue
        if locus.startswith(("*P","@P")):paragraph+=1
        txt=re.sub(r"<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]","",m[5])
        first=re.split(r"[.,\s]+",txt.lstrip("% ").strip())[0].lower()
        first=re.sub("[^a-z]","",first)
        if first:groups[(current,paragraph)].append((int(m[3]),first))
    return groups
def count(groups):
    numerator=denominator=0
    for seq in groups.values():
        seq=sorted(seq)
        for (i,a),(j,b) in zip(seq,seq[1:]):
            if j!=i+1:continue
            if a.startswith("qo"):
                denominator+=1
                numerator+=b.startswith("qo")
    return numerator,denominator
def permute(groups,model,rng):
    out={}
    if model=="within_paragraph":
        for k,v in groups.items():
            words=[w for _,w in v];rng.shuffle(words)
            out[k]=[(v[i][0],w) for i,w in enumerate(words)]
    elif model=="within_folio":
        byleaf=collections.defaultdict(list)
        for k,v in groups.items():
            for _,w in v:byleaf[int(re.match(r"f(\d+)",k[0])[1])].append(w)
        for words in byleaf.values():rng.shuffle(words)
        cursor=collections.Counter()
        for k,v in groups.items():
            leaf=int(re.match(r"f(\d+)",k[0])[1]);n=len(v);start=cursor[leaf]
            out[k]=[(v[i][0],w) for i,w in enumerate(byleaf[leaf][start:start+n])]
            cursor[leaf]+=n
    else:raise ValueError(model)
    return out
def main():
    groups=parse()
    if not groups:raise SystemExit("FAIL CLOSED: no training data parsed")
    obs,den=count(groups)
    rng=random.Random(SEED)
    models={}
    for model in ("within_paragraph","within_folio"):
        sims=[count(permute(groups,model,rng)) for _ in range(REPS)]
        rates=sorted([n/d for n,d in sims if d>0])
        if len(rates)!=REPS or den==0:raise SystemExit("FAIL CLOSED: zero qo denominator")
        observed_rate=obs/den
        p=(1+sum(x<=observed_rate for x in rates))/(REPS+1)
        models[model]={"null_mean_rate":sum(rates)/REPS,"null_95_rate":[rates[49],rates[1949]],"observed_rate":observed_rate,"p_depletion":p,
                       "holm_2":None}
    ps=sorted(models,key=lambda x:models[x]["p_depletion"])
    models[ps[0]]["holm_2"]=min(1,2*models[ps[0]]["p_depletion"])
    models[ps[1]]["holm_2"]=max(models[ps[0]]["holm_2"],models[ps[1]]["p_depletion"])
    result={"classification":"EXPLORATORY_NOT_VALIDATED","preregistered_protocol":"research/qo-rival-protocol.md",
            "seed":SEED,"replicates_per_model":REPS,"input_sha256":SHA,
            "metric":"conditional rate P(next qo | current qo), among adjacent P lines; denominator recalculated per permutation",
            "training_groups":len(groups),"observed_qo_to_qo":obs,"eligible_qo_pairs":den,
            "null_models":models,"generated_at":datetime.now(timezone.utc).isoformat(),
            "holdout":"excluded from metrics; complete file read solely for SHA256; no holdout evaluation",
            "caveat":"Two simple shuffle rivals are not generator-level controls. No independent validation or decipherment claim."}
    dest=ROOT/"research-output";dest.mkdir(exist_ok=True)
    (dest/"qo-rival.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["classification"],"observed":obs,"eligible":den,"models":models},indent=2))
if __name__=="__main__":main()
