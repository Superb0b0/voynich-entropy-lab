#!/usr/bin/env python3
"""Exploratory robustness check; no protected IDs or text in output."""
import json, re, statistics
from anchor01_semantic_probe import ROOT, hashes, protected, read_pages

def summarize(pages, common):
    out={}
    for page in common:
        folio=int(re.match(r"f(\d+)",page).group(1))
        section="zodiac" if 70<=folio<=73 else "herbal" if 1<=folio<=57 else None
        if section is None:continue
        tokens=pages[page]
        if len(tokens)<75:continue
        out[page]={"folio":folio,"section":section,
                   "all":sum(t.startswith("qo") for t in tokens)/len(tokens),
                   "long":sum(t.startswith("qo") for t in tokens if len(t)>=5)/max(1,sum(len(t)>=5 for t in tokens)),
                   "nlong":sum(len(t)>=5 for t in tokens)}
    return out

def report(s):
    # Aggregate by folio to avoid treating multiple panels as independent units.
    byfolio={}
    for p,v in s.items():byfolio.setdefault(v["folio"],[]).append(v)
    folios={k:{"section":v[0]["section"],
               "all":statistics.mean(x["all"] for x in v),
               "long":statistics.mean(x["long"] for x in v)} for k,v in byfolio.items()}
    result={}
    for metric in ("all","long"):
        z=[v[metric] for v in folios.values() if v["section"]=="zodiac"]
        h=[v[metric] for v in folios.values() if v["section"]=="herbal"]
        if len(z)<2 or len(h)<10:raise RuntimeError("insufficient folios")
        result[metric]={"zodiac_folios":len(z),"herbal_folios":len(h),
                        "zodiac_mean":round(statistics.mean(z),8),
                        "herbal_mean":round(statistics.mean(h),8),
                        "difference":round(statistics.mean(z)-statistics.mean(h),8)}
    return result

def main():
    hashes()
    excluded=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two corpora required")
    pages=[read_pages(s,excluded) for s in sources]
    common=set(pages[0])&set(pages[1])
    if not common:raise RuntimeError("no shared permitted pages")
    a=report(summarize(pages[0],common))
    b=report(summarize(pages[1],common))
    print(json.dumps({"status":"EXPLORATORY_ROBUSTNESS_ONLY",
      "transcriptions":[{"source":sources[0].name,"results":a},
                        {"source":sources[1].name,"results":b}],
      "shared_pages":len(common),"discordant_pages_excluded":len(set(pages[0])^set(pages[1])),
      "warning":"qo is a literal prefix; cross-transcription encoding equivalence is NOT established; comparisons are descriptive, not a replication",
      "independence":"folio aggregation; no holdout or hand/layout adjustment"},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
