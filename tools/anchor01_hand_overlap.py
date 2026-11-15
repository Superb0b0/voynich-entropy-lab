#!/usr/bin/env python3
"""Independent IVTFF $H (Davis hand) x $I (illustration) overlap gate.
Only aggregate counts, never protected page IDs, page text, or labels.
"""
import json,re
from anchor01_semantic_probe import ROOT,hashes,protected,sanitize,read_pages
HEADER=re.compile(r"^<(f\d+[rv]\d*)>\s+<!([^>]*)>")
FIELD=re.compile(r"\$([HI])=([A-Za-z0-9@])")
def metadata(source,forbidden):
    result={}
    for line in sanitize(source.read_text(),forbidden).splitlines():
        m=HEADER.match(line)
        if not m:continue
        fields=dict(FIELD.findall(m.group(2)))
        if fields.get("H") in "12345" and fields.get("I") in ("H","Z","A","B","C","P","S","T"):
            result[m.group(1)]=(fields["H"],fields["I"])
    return result
def main():
    hashes();forbidden=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two corpora required")
    pages=[read_pages(s,forbidden) for s in sources]
    meta=[metadata(s,forbidden) for s in sources]
    common=set(pages[0])&set(pages[1])&set(meta[0])&set(meta[1])
    eligible=[p for p in common if len(pages[0][p])>=75 and len(pages[1][p])>=75
              and meta[0][p]==meta[1][p]]
    by={}
    for p in eligible:
        hand,illustration=meta[0][p]
        by.setdefault(hand,{}).setdefault(illustration,0)
        by[hand][illustration]+=1
    # The original contrast is herbal H versus zodiac Z. Require actual
    # overlap of independent scribal labels, not proxy folio-number inference.
    overlaps={hand:{"herbal_pages":cats.get("H",0),"zodiac_pages":cats.get("Z",0)}
              for hand,cats in by.items() if cats.get("H",0)>0 and cats.get("Z",0)>0}
    alternative={hand:{k:v for k,v in sorted(cats.items()) if v>=3}
                 for hand,cats in by.items() if sum(v>=3 for v in cats.values())>=2}
    print(json.dumps({"status":"ORIGINAL_CONTRAST_IDENTIFIABLE" if overlaps else "ORIGINAL_CONTRAST_NOT_IDENTIFIABLE",
      "eligible_pages_with_agreed_hand_and_illustration":len(eligible),
      "same_hand_herbal_zodiac_overlap":overlaps,
      "alternative_within_hand_section_pairs_3plus_pages":alternative,
      "metadata":"IVTFF page header $H and $I; both transcriptions must agree",
      "holdout":"excluded before metadata and token parsing",
      "limitation":"page counts only; a different section pair requires preregistration before statistical test"},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
