#!/usr/bin/env python3
"""Hand-2 H/B length-standardized exploratory sensitivity; protected folios excluded."""
import json,random,statistics
from anchor01_semantic_probe import ROOT,hashes,protected,read_pages,SEED
from anchor01_hand_overlap import metadata
B=9999
def binid(t):
    n=len(t)
    return 0 if n<=3 else 1 if n<=5 else 2
def evaluate(pages,meta):
    selected={p:(cat,pages[p]) for p,(hand,cat) in meta.items() if hand=="2" and cat in ("H","B") and len(pages[p])>=75}
    groups={g:[(p,t) for p,(c,t) in selected.items() if c==g] for g in ("H","B")}
    if min(map(len,groups.values()))<10:raise RuntimeError("insufficient pages")
    counts=[sum(binid(t)==b for _,tokens in selected.values() for t in tokens) for b in range(3)]
    total=sum(counts);weights=[v/total for v in counts]
    rates={}
    for g,items in groups.items():
        rr=[]
        for _,tokens in items:
            bins=[[t for t in tokens if binid(t)==b] for b in range(3)]
            if any(not x for x in bins):raise RuntimeError("empty length bin on eligible page")
            rr.append(sum(w*sum(t.startswith("qo") for t in bb)/len(bb) for w,bb in zip(weights,bins)))
        rates[g]=rr
    obs=statistics.mean(rates["B"])-statistics.mean(rates["H"])
    vals=rates["H"]+rates["B"];nh=len(rates["H"]);rng=random.Random(SEED);extreme=0
    for _ in range(B):
        inds=set(rng.sample(range(len(vals)),nh))
        diff=sum(v for i,v in enumerate(vals) if i not in inds)/(len(vals)-nh)-sum(vals[i] for i in inds)/nh
        extreme+=abs(diff)>=abs(obs)-1e-15
    return {"botanical_pages":nh,"biological_pages":len(rates["B"]),
       "botanical_standardized":round(statistics.mean(rates["H"]),8),
       "biological_standardized":round(statistics.mean(rates["B"]),8),
       "difference":round(obs,8),"permutation_p":round((extreme+1)/(B+1),6),
       "length_bins":"1-3,4-5,6+; pooled token weights"}
def main():
    hashes();forbidden=protected();sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two sources required")
    pages=[read_pages(s,forbidden) for s in sources]
    metas=[metadata(s,forbidden) for s in sources]
    common=set(pages[0])&set(pages[1])&set(metas[0])&set(metas[1])
    agreed={p:metas[0][p] for p in common if metas[0][p]==metas[1][p] and min(len(pages[0][p]),len(pages[1][p]))>=75}
    result={s.name:evaluate(pg,agreed) for s,pg in zip(sources,pages)}
    print(json.dumps({"status":"EXPLORATORY_LENGTH_CONTROL_NOT_VALIDATED","test":"within_hand2_biological_vs_botanical_length_standardized_qo",
       "results":result,"permutations":B,"seed":SEED,
       "limitations":["length bins coarse","page permutation ignores folio clustering","no layout control",
       "no independent holdout","no multiplicity correction","not a translation"]},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
