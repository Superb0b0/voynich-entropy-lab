#!/usr/bin/env python3
"""Preregistered hand-2 H versus B exploratory qo test. Protected pages excluded."""
import json,random,statistics
from anchor01_semantic_probe import ROOT,hashes,protected,read_pages,SEED
from anchor01_hand_overlap import metadata
B=9999
def evaluate(pages,meta,shared):
    rows=[]
    for p in shared:
        hand,section=meta[p]
        if hand!="2" or section not in ("H","B") or len(pages[p])<75:continue
        tokens=pages[p]
        rate=sum(t.startswith("qo") for t in tokens)/len(tokens)
        rows.append((section,rate))
    h=[v for k,v in rows if k=="H"];b=[v for k,v in rows if k=="B"]
    if len(h)<10 or len(b)<10:raise RuntimeError("insufficient within-hand pages")
    obs=statistics.mean(b)-statistics.mean(h)
    vals=h+b;nh=len(h);rng=random.Random(SEED);extreme=0
    for _ in range(B):
        indices=set(rng.sample(range(len(vals)),nh))
        d=sum(vals[i] for i in range(len(vals)) if i not in indices)/len(b)-sum(vals[i] for i in indices)/nh
        extreme+=abs(d)>=abs(obs)-1e-15
    return {"botanical_pages":len(h),"biological_pages":len(b),
            "botanical_mean":round(statistics.mean(h),8),"biological_mean":round(statistics.mean(b),8),
            "difference_biological_minus_botanical":round(obs,8),
            "page_permutation_p":round((extreme+1)/(B+1),6)}
def main():
    hashes();excluded=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two sources required")
    pages=[read_pages(s,excluded) for s in sources]
    metas=[metadata(s,excluded) for s in sources]
    shared=set(pages[0])&set(pages[1])&set(metas[0])&set(metas[1])
    agreed={p:metas[0][p] for p in shared if metas[0][p]==metas[1][p] and len(pages[0][p])>=75 and len(pages[1][p])>=75}
    result={s.name:evaluate(pg,agreed,agreed) for s,pg in zip(sources,pages)}
    print(json.dumps({"status":"EXPLORATORY_WITHIN_HAND_NOT_VALIDATED",
      "hypothesis":"hand 2 biological and botanical pages have different qo-prefix rates",
      "groups":"IVTFF $H=2, $I=H versus $I=B, both transcriptions agree",
      "seed":SEED,"permutations":B,"results":result,
      "limitations":["page rather than folio permutation","section may be confounded with layout and vocabulary",
      "no independent holdout","two transcriptions not independent","no multiple-testing adjustment",
      "not semantic translation"]},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
