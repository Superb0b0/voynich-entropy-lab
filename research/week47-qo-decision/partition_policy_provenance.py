#!/usr/bin/env python3
"""Independent, aggregate-only policy derivation. NEVER read or write HOLDOUT.md.

Cross-check immutable make_holdout.py algorithm with W47's literal policy.
Reads the canonical ZL3b raw bytes solely to derive page-header strata and
compare a computed set in memory; never prints protected identifiers.
This verifies policy reproducibility, NOT an independent scientific holdout.
"""
import argparse
import ast
import collections
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_CORPUS = "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
FROZEN_SELECTOR_BLOB = "7987a4b70fc1c78735beb69ffb8745b6edfd16ff"
FROZEN_POLICY_BLOB = "f06bbf1d3ed8357153d634cc424e65966d184625"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def load_literal_assignment(source, name):
    """Use AST literals only; do not import/execute source with side effects."""
    matches=[]
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for lhs in node.targets:
                if isinstance(lhs, ast.Name) and lhs.id==name:
                    matches.append(ast.literal_eval(node.value))
    if len(matches)!=1:
        raise RuntimeError("Required fixed policy literal missing or ambiguous: "+name)
    return matches[0]

def derive_partition(raw, seed, fraction):
    """Independent implementation of make_holdout.py's documented selection."""
    if type(seed) is not int or not 0 < fraction < 1:
        raise RuntimeError("Invalid selector parameters")
    page_re = re.compile(r"^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>", re.M)
    leaf_re = re.compile(r"^f(\d+)")
    lang_re = re.compile(r"\$L=([A-Za-z])")
    leaves=collections.defaultdict(list)
    for match in page_re.finditer(raw.decode("utf-8")):
        page,attrs=match.groups()
        leaf=int(leaf_re.match(page).group(1))
        lm=lang_re.search(attrs)
        leaves[leaf].append(lm.group(1) if lm else "?")
    if not leaves:
        raise RuntimeError("No recognized page headers")
    strata=collections.defaultdict(list)
    for leaf,langs in sorted(leaves.items()):
        counts=collections.Counter(l for l in langs if l in "AB")
        cls=counts.most_common(1)[0][0] if counts else "other"
        strata[cls].append(leaf)
    rng=random.Random(seed)
    result=[]
    for key in sorted(strata):
        members=strata[key]
        k=max(1,round(len(members)*fraction))
        result.extend(rng.sample(members,k))
    return set(result),len(leaves),len(strata)

def audit(selector_path, policy_path, corpus_path):
    selector=selector_path.read_bytes()
    policy=policy_path.read_bytes()
    corpus=corpus_path.read_bytes()
    if blob_sha(selector)!=FROZEN_SELECTOR_BLOB:
        raise RuntimeError("Selector Git blob changed; refuse unregistered provenance")
    if blob_sha(policy)!=FROZEN_POLICY_BLOB:
        raise RuntimeError("W47 policy Git blob changed; refuse unregistered provenance")
    if sha(corpus)!=CANONICAL_CORPUS:
        raise RuntimeError("Corpus SHA-256 mismatch")
    seed=load_literal_assignment(selector.decode("utf-8"),"SEED")
    fraction=load_literal_assignment(selector.decode("utf-8"),"FRACTION")
    if seed!=20261114 or fraction!=.2:
        raise RuntimeError("Selection seed or fraction mismatch")
    literal=load_literal_assignment(policy.decode("utf-8"),"HELD")
    if not isinstance(literal,set) or not literal or any(type(v) is not int for v in literal):
        raise RuntimeError("Invalid W47 static partition literal")
    derived,n_folios,n_strata=derive_partition(corpus,seed,fraction)
    if literal!=derived:
        # No IDs or asymmetric set differences printed.
        raise RuntimeError("PARTITION_NOT_ATTESTED: original selector and W47 policy DISAGREE")
    return {
      "status":"REPRODUCED_SELECTOR_MATCH",
      "audit_scope":"W47 static exclusions vs original source algorithm; NOT independent holdout",
      "corpus_sha256":CANONICAL_CORPUS,
      "selector_source_sha256":sha(selector),
      "policy_source_sha256":sha(policy),
      "selector_seed":seed,
      "selector_fraction":fraction,
      "source_folios":n_folios,
      "source_strata":n_strata,
      "excluded_folio_count":len(derived),
      "identifiers_exported":False,
      "holdout_file_read":False,
      "input_data_exported":False,
      "limitations":[
        "Source algorithm provenance is Git, not a trusted external timestamp",
        "No comparison to HOLDOUT.md contents, no independent blind holdout",
        "Only the known frozen selector and literal policy versions were checked",
        "Scientific endpoint not evaluated"
      ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--selector",type=Path,required=True)
    p.add_argument("--policy",type=Path,required=True)
    p.add_argument("--corpus",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    report=audit(args.selector,args.policy,args.corpus)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("limitations",)},sort_keys=True))
    return 0

if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Exception must never contain a held folio ID.
        print(f"FAIL CLOSED: {exc.__class__.__name__}: {exc}",file=sys.stderr)
        sys.exit(1)
