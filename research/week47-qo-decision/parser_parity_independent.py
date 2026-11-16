#!/usr/bin/env python3
"""Independent RC1.2-vs-IVTFF replay: no protected names/text in output.

The second tokenizer and block scanner are written separately from canonical
RC1.2 and from structural_audit.census. Both references are hash-locked.
Full-corpus structure is checked, NOT a scientific hypothesis/holdout test.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
ZL3B="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
IT2A="7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"
PARSER="8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5"
P_TAGS={"*P0","*Pb","+P0","+P1","+Pb","+Pc","+Pr","=P0","=Pt","@P0","@P1","@Pb"}
TOKEN=re.compile(r"[A-Za-z]+")
MARKERS=("<$>","<%>","<->","<~>","<d>","<@H=2>","<@H=3>")
HEADER=re.compile(r"^<([^>]+)>[ \t]*(.*)$")
COMMENT=re.compile(r"<![^>]*>")
FOLIO=re.compile(r"f(?:[0-9]+[rv][0-9]*|Ros)")
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
def independent_tokens(body):
    """Independent alternate cleaner, comments before markers, no reading choice."""
    without_comments=COMMENT.sub(" ",body)
    cleaned=without_comments
    for mark in MARKERS:
        cleaned=cleaned.replace(mark," ")
    cleaned=re.sub(r"\[[^\[\]]*\]"," ",cleaned)
    cleaned=cleaned.replace("{","").replace("}","")
    return [x.lower() for x in TOKEN.findall(cleaned)],without_comments

def scan(path,canonical):
    raw=path.read_bytes()
    records=canonical.parse_corpus(path,verify_source=False)["records"]
    by_physical={r["physical_line"]:r for r in records}
    blocks=[];pairs=[];current=None;inside=0;outside=0;page=None
    live=None;last_page=None;observed=0;lex_mismatch=0;locator_mismatch=0
    hidden_markers=0;extra=0;marker_open=0;marker_close=0
    for n,src in enumerate(raw.decode("utf-8").splitlines(),1):
        match=HEADER.match(src)
        if not match:
            if n in by_physical:locator_mismatch+=1
            continue
        key,body=match.groups()
        if "," not in key:
            if FOLIO.fullmatch(key):
                page=key
            continue
        loc,tag=key.split(",",1)
        if tag not in P_TAGS:
            continue
        observed+=1
        r=by_physical.get(n)
        if r is None or r["locus_id"]!=loc or r["folio"]!=loc.split(".")[0]:
            locator_mismatch+=1
        tokens,uncommented=independent_tokens(body)
        if r is None or tokens!=r["tokens"]:
            lex_mismatch+=1
        if ("<%>" in body and "<%>" not in uncommented) or ("<$>" in body and "<$>" not in uncommented):
            hidden_markers+=1
        if page!=loc.split(".")[0]:
            locator_mismatch+=1
        # The *independent* scanner respects both physical and locus adjacency.
        line=int(loc.rsplit(".",1)[-1])
        if live is not None and page!=last_page:
            extra+=1;live=None
        begin="<%>" in uncommented
        end="<$>" in uncommented
        if begin:
            marker_open+=1
            if live is not None:extra+=1
            live=dict(page=page,start=loc,rows=[],language=None)
        if live is not None:
            live["rows"].append((n,loc,line))
            inside+=1
        else:outside+=1
        if end:
            marker_close+=1
            if live is None:extra+=1
            else:
                marker=(live["page"],live["start"],loc,
                        live["rows"][0][0],n,len(live["rows"]))
                blocks.append(marker)
                for u,v in zip(live["rows"],live["rows"][1:]):
                    if v[0]==u[0]+1 and v[2]==u[2]+1:
                        pairs.append((page,live["start"],loc,u[1],v[1]))
            live=None
        last_page=page
    if live is not None:extra+=1
    return dict(
      rows=observed,canonical_rows=len(records),
      original_tokens=sum(len(r["tokens"]) for r in records),
      original_types=len({tok for r in records for tok in r["tokens"]}),
      locator_mismatches=locator_mismatch,token_mismatches=lex_mismatch,
      markers_inside_comments=hidden_markers,block_exceptions=extra,
      blocks=len(blocks),open_markers=marker_open,close_markers=marker_close,
      in_blocks=inside,outside_blocks=outside,adjacent_pairs=len(pairs),
      private_blocks=blocks,private_pairs=pairs)

def validate_one(path,source_sha,canonical,structural,full):
    raw=path.read_bytes()
    if sha(raw)!=source_sha:raise RuntimeError("Canonical input digest mismatch")
    indie=scan(path,canonical)
    origin=structural.census(path,canonical,full=full)
    # Ignore only language field of reference block for boundary parity; check
    # page/start/end, physical start/end and P count.
    old=[tuple(row[:6]) for row in origin["block_ids"]]
    oldpairs=[tuple(row) for row in origin["pair_ids"]]
    result={k:v for k,v in indie.items() if not k.startswith("private_")}
    result["canonical_source_sha256"]=source_sha
    result["boundary_mismatches"]=len(set(indie["private_blocks"])^set(old))
    result["pair_eligibility_mismatches"]=len(set(indie["private_pairs"])^set(oldpairs))
    result["duplicated_boundary_count"]=len(indie["private_blocks"])-len(set(indie["private_blocks"]))
    result["duplicated_pair_count"]=len(indie["private_pairs"])-len(set(indie["private_pairs"]))
    result["canonical_reference_block_count"]=origin["blocks"]
    result["canonical_reference_pair_count"]=len(oldpairs)
    result["reference_outside_blocks"]=origin["P_loci_outside_blocks"]
    result["passed"]=bool(result["rows"]==result["canonical_rows"] and
       not any(result[x] for x in (
       "locator_mismatches","token_mismatches","boundary_mismatches",
       "pair_eligibility_mismatches","block_exceptions",
       "duplicated_boundary_count","duplicated_pair_count"))
       and result["outside_blocks"]==origin["P_loci_outside_blocks"])
    return result,indie

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--zl3b",type=Path,required=True)
    a.add_argument("--it2a",type=Path,required=True)
    a.add_argument("--parser",type=Path,required=True)
    a.add_argument("--structural",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    if sha(args.parser.read_bytes())!=PARSER:
        raise RuntimeError("Canonical parser SHA mismatch")
    canonical=load(args.parser,"w47_canonical")
    structural=load(args.structural,"w47_structure_reference")
    if canonical.run_unit_tests():raise RuntimeError("Canonical parser unit tests failed")
    z,zi=validate_one(args.zl3b,ZL3B,canonical,structural,True)
    it,ii=validate_one(args.it2a,IT2A,canonical,structural,False)
    common_blocks=set(zi["private_blocks"])&set(ii["private_blocks"])
    common_pairs=set(zi["private_pairs"])&set(ii["private_pairs"])
    report={
      "classification":"TECHNICAL_SECOND_IMPLEMENTATION_NOT_INDEPENDENT_HOLDOUT",
      "canonical_parser_sha256":PARSER,
      "zl3b":z,"it2a":it,
      "matching_block_geometry":len(common_blocks),
      "matching_pairs":len(common_pairs),
      "all_parity_checks_passed":z["passed"] and it["passed"],
      "identifiers_exported":False,"tokens_exported":False,"holdout_file_read":False,
      "limitations":["Original reference and second implementation in one CI ecosystem",
       "Transliteration robustness is not an independent manuscript replication",
       "No protected partition or runner scientific approval in this report"]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("classification","matching_block_geometry","matching_pairs","all_parity_checks_passed","identifiers_exported")},sort_keys=True))
    if not report["all_parity_checks_passed"]:
        raise RuntimeError("INDEPENDENT_PARSER_PARITY_FAILED: see aggregate report")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("FAIL CLOSED (no protected IDs):",type(exc).__name__,file=sys.stderr)
        sys.exit(1)
