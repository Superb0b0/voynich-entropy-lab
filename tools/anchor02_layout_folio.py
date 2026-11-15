#!/usr/bin/env python3
"""Hand-2 H/B folio-cluster and line-position sensitivity. No protected text output."""
import json,re,random,statistics
from anchor01_semantic_probe import ROOT,hashes,protected,sanitize,SEED
from anchor01_hand_overlap import metadata
PAGE=re.compile(r"^<(f\d+[rv]\d*)>\s+<!")
LINE=re.compile(r"^<f\d+[rv]\d*\.[^>]+>\s+(.*)")
TOKEN=re.compile(r"[a-z]+",re.I)
B=9999
def read(source,excluded):
    out={};current=None
    for line in sanitize(source.read_text(),excluded).splitlines():
        m=PAGE.match(line)
        if m:current=m.group(1);out.setdefault(current,[]);continue
        if current is None:continue
        m=LINE.match(line)
        if m:
            words=TOKEN.findall(m.group(1).lower())
            if words:out[current].append(words)
    return out
def folio(p):return re.match(r"f\d+",p).group()
def analyze(pages,labels):
    selected={p:(labels[p][1],pages[p]) for p in labels if labels[p][0]=="2" and labels[p][1] in ("H","B") and sum(map(len,pages[p]))>=75}
    # aggregate first/last/interior line positions separately; avoids treating line-end patterns as content
    rates={};folio_groups={}
    for p,(g,lines) in selected.items():
        bins=[[],[],[]]
        for words in lines:
            for i,t in enumerate(words):
                b=0 if i==0 else 2 if i==len(words)-1 else 1
                bins[b].append(t)
        if any(len(b)==0 for b in bins):raise RuntimeError("empty line position")
        # fixed equal weighting across line positions
        rate=sum(sum(t.startswith("qo") for t in b)/len(b) for b in bins)/3
        folio_groups.setdefault(folio(p),[]).append((g,rate))
    for f,rows in folio_groups.items():
        groups={g for g,_ in rows}
        if len(groups)!=1:raise RuntimeError("mixed section within folio")
        rates[f]=(rows[0][0],statistics.mean(v for _,v in rows))
    H=[v for g,v in rates.values() if g=="H"];Bv=[v for g,v in rates.values() if g=="B"]
    if min(len(H),len(Bv))<5:raise RuntimeError("insufficient independent folios")
    obs=statistics.mean(Bv)-statistics.mean(H)
    vals=H+Bv;nh=len(H);rng=random.Random(SEED);extreme=0
    for _ in range(B):
        inds=set(rng.sample(range(len(vals)),nh))
        diff=sum(v for i,v in enumerate(vals) if i not in inds)/(len(vals)-nh)-sum(vals[i] for i in inds)/nh
        extreme+=abs(diff)>=abs(obs)-1e-15
    loo=[]
    for j in range(len(H)):
        loo.append(statistics.mean(Bv)-statistics.mean(H[:j]+H[j+1:]))
    for j in range(len(Bv)):
        loo.append(statistics.mean(Bv[:j]+Bv[j+1:])-statistics.mean(H))
    return {"botanical_folios":len(H),"biological_folios":len(Bv),
        "botanical_pages":sum(g=="H" for g,_ in selected.values()),
        "biological_pages":sum(g=="B" for g,_ in selected.values()),
        "position_standardized_folio_difference":round(obs,8),
        "folio_permutation_p":round((extreme+1)/(B+1),6),
        "leave_one_folio_out_min_difference":round(min(loo),8),
        "leave_one_folio_out_max_difference":round(max(loo),8)}
def main():
    hashes();excluded=protected();sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two corpora required")
    pages=[read(s,excluded) for s in sources];meta=[metadata(s,excluded) for s in sources]
    common=set(pages[0])&set(pages[1])&set(meta[0])&set(meta[1])
    labels={p:meta[0][p] for p in common if meta[0][p]==meta[1][p] and min(sum(map(len,pages[0][p])),sum(map(len,pages[1][p])))>=75}
    results={s.name:analyze(pg,labels) for s,pg in zip(sources,pages)}
    print(json.dumps({"status":"EXPLORATORY_LAYOUT_FOLIO_NOT_VALIDATED","results":results,
       "permutations":B,"seed":SEED,"line_positions":"first,interior,last; equal weighting",
       "limits":["simple parser and editorial markup","folio permutation may not remove quire clustering",
       "no untouched holdout","not semantic validation"]},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
