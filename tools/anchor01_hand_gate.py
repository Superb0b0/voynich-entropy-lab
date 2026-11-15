#!/usr/bin/env python3
"""Fail-closed identifiability gate for the existing zodiac-vs-herbal qo contrast.
Uses published Davis hand attribution at section level; does NOT invent per-page labels.
No protected text, folio identifiers or hand inference from the target statistic.
"""
import json
from anchor01_semantic_probe import ROOT,hashes,protected,read_pages
def main():
    hashes(); forbidden=protected()
    sources=sorted((ROOT/"data").glob("*.txt"))
    if len(sources)!=2:raise RuntimeError("two attested corpora required")
    pages=[read_pages(p,forbidden) for p in sources]
    common=set(pages[0])&set(pages[1])
    # Explicit literature: Davis Hand 4 is zodiac/astronomical/cosmological;
    # botanical folios are Hands 1, 2, 3, 5. Folio-specific exceptions
    # must be resolved from independent page-level labels, not guessed.
    zodiac=[p for p in common if 70<=int(p[1:].split("r")[0].split("v")[0])<=73 and len(pages[0][p])>=75]
    herbal=[p for p in common if 1<=int(p[1:].split("r")[0].split("v")[0])<=57 and len(pages[0][p])>=75]
    if len(zodiac)<3 or len(herbal)<10:raise RuntimeError("original eligible groups not reproduced")
    print(json.dumps({"status":"NOT_IDENTIFIABLE_HAND_CONFOUNDED",
      "test":"within_hand_section_identifiability",
      "eligible_zodiac_pages":len(zodiac),"eligible_herbal_pages":len(herbal),
      "same_hand_zodiac_herbal_pairs_supported_by_section_level_attribution":0,
      "causal_section_effect_estimable":False,
      "decision":"Do not interpret qo contrast as section semantics or as hand-independent",
      "basis":"Davis hand 4 covers zodiac/astronomical/cosmological; herbal attributed to other hands",
      "source":"https://www.voynich.nu/writing.html",
      "caveat":"section-level attribution only; full per-folio attribution not independently ingested",
      "holdout":"protected folios excluded; no holdout evaluation"},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"NON_VERIFICATO","error":str(e)}))
        raise SystemExit(1)
