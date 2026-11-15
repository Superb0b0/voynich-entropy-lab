#!/usr/bin/env python3
"""Exploratory, training-only zodiac vs herbal text test. Never prints page IDs or text."""
import hashlib, json, math, pathlib, random, re, statistics, tempfile
from verify_attempts import ROOT, hashes, protected, sanitize

PAGE=re.compile(r"^<(f(\d+)[rv]\d*)>\s+<!")
LINE=re.compile(r"^<f\d+[rv]\d*\.[^>]+>\s+(.*)")
TOKEN=re.compile(r"[a-z]+",re.I)
SEED=20261115
def read_pages(source,excluded):
    raw=source.read_text()
    filtered=sanitize(raw,excluded)
    pages={}; current=None
    for line in filtered.splitlines():
        m=PAGE.match(line)
        if m:
            current=m.group(1);pages.setdefault(current,[]);continue
        if current is None:continue
        m=LINE.match(line)
        if m:
            pages[current].extend(TOKEN.findall(m.group(1).lower()))
    return pages

def test():
    hashes()
    forbidden=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("expected exactly two attested corpora")
    page_sets=[read_pages(p,forbidden) for p in sources]
    common=set(page_sets[0]) & set(page_sets[1])
    if not common:raise RuntimeError("no common permitted pages")
    # Illustrative section classification fixed before testing.
    # Zodiac: folios 70-73; botanical control: folios 1-57.
    # Both are rough codicological proxies, not independent iconographic labels.
    groups={}
    for page in sorted(common):
        n=int(re.match(r"f(\d+)",page).group(1))
        label="zodiac" if 70<=n<=73 else "herbal" if 1<=n<=57 else None
        if label is None:continue
        tokens=page_sets[0][page]
        if len(tokens)<75:continue
        # Prespecified simple EVA prefix proxy, not a word translation.
        rate=sum(t.startswith("qo") for t in tokens)/len(tokens)
        groups[page]=(label,rate,n)
    zodiac=[v[1] for v in groups.values() if v[0]=="zodiac"]
    herbal=[v[1] for v in groups.values() if v[0]=="herbal"]
    if len(zodiac)<3 or len(herbal)<10:
        raise RuntimeError("insufficient permitted eligible pages for prespecified test")
    obs=statistics.mean(zodiac)-statistics.mean(herbal)
    vals=[v[1] for v in groups.values()]
    nz=len(zodiac);rng=random.Random(SEED)
    # Monte Carlo label permutation; exploratory only, section/hand confounded.
    exceed=0;B=9999
    for _ in range(B):
        idx=set(rng.sample(range(len(vals)),nz))
        a=sum(vals[i] for i in idx)/nz
        b=sum(vals[i] for i in range(len(vals)) if i not in idx)/(len(vals)-nz)
        exceed+=abs(a-b)>=abs(obs)-1e-15
    result={"status":"EXPLORATORY_NOT_SEMANTIC","test":"qo_prefix_zodiac_vs_herbal","seed":SEED,
            "n_zodiac_pages":len(zodiac),"n_herbal_pages":len(herbal),
            "discordant_pages_excluded":len(set(page_sets[0])^set(page_sets[1])),
            "mean_zodiac":round(statistics.mean(zodiac),8),
            "mean_herbal":round(statistics.mean(herbal),8),
            "difference":round(obs,8),"permutation_p_two_sided":round((exceed+1)/(B+1),6),
            "limitations":["no independent visual labeling","section/hand confounding","not a translation",
                           "no independent holdout","full verifier remains separate"]}
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    try:test()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
