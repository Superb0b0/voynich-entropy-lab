#!/usr/bin/env python3
"""Exploratory length-standardized qo contrast with folio-level permutations.
No protected text, identifiers, or individual folios are printed."""
import json,random,re,statistics
from anchor01_semantic_probe import ROOT,hashes,protected,read_pages,SEED

B=9999
def analyze(pages,shared):
    folios={}
    for page in shared:
        n=int(re.match(r"f(\d+)",page).group(1))
        group="zodiac" if 70<=n<=73 else "herbal" if 1<=n<=57 else None
        if not group or len(pages[page])<75:continue
        folios.setdefault(n,{"group":group,"bins":[[0,0] for _ in range(3)]})
        for t in pages[page]:
            k=0 if len(t)<=3 else 1 if len(t)<=5 else 2
            folios[n]["bins"][k][1]+=1
            folios[n]["bins"][k][0]+=int(t.startswith("qo"))
    z=[v for v in folios.values() if v["group"]=="zodiac"]
    h=[v for v in folios.values() if v["group"]=="herbal"]
    if len(z)<3 or len(h)<10:raise RuntimeError("insufficient folios")
    # Common pooled length distribution. Equal weight per folio within each group.
    totals=[sum(v["bins"][k][1] for v in folios.values()) for k in range(3)]
    if min(totals)==0:raise RuntimeError("empty length stratum")
    weights=[t/sum(totals) for t in totals]
    eligible=[v for v in folios.values() if all(pair[1]>0 for pair in v["bins"])]
    z=[v for v in eligible if v["group"]=="zodiac"]
    h=[v for v in eligible if v["group"]=="herbal"]
    if len(z)<3 or len(h)<10:raise RuntimeError("insufficient folios with all length strata")
    def rate(v):return sum(weights[k]*v["bins"][k][0]/v["bins"][k][1] for k in range(3))
    a=[rate(v) for v in z];b=[rate(v) for v in h]
    diff=statistics.mean(a)-statistics.mean(b)
    values=a+b;nz=len(a);rng=random.Random(SEED);extreme=0
    for _ in range(B):
        idx=set(rng.sample(range(len(values)),nz))
        d=sum(values[i] for i in idx)/nz-sum(values[i] for i in range(len(values)) if i not in idx)/(len(values)-nz)
        extreme+=abs(d)>=abs(diff)-1e-15
    return {"zodiac_folios":len(z),"herbal_folios":len(h),
      "zodiac_standardized_rate":round(statistics.mean(a),8),
      "herbal_standardized_rate":round(statistics.mean(b),8),
      "difference":round(diff,8),"folio_permutation_p":round((extreme+1)/(B+1),6),
      "length_bin_weights":[round(w,6) for w in weights]}
def main():
    hashes();excluded=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two sources required")
    pages=[read_pages(s,excluded) for s in sources]
    shared=set(pages[0])&set(pages[1])
    if not shared:raise RuntimeError("no shared permitted pages")
    results={p.name:analyze(data,shared) for p,data in zip(sources,pages)}
    print(json.dumps({"status":"EXPLORATORY_NOT_VALIDATED","test":"folio_permutation_length_standardization",
      "seed":SEED,"permutations":B,"results":results,
      "limitations":["section/hand confounding remains","no independent holdout",
      "two transcriptions are not independent samples","cross-transcription qo equivalence unverified",
      "not a semantic translation"]},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
