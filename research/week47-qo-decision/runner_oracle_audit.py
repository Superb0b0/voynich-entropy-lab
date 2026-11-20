#!/usr/bin/env python3
"""Independent analytic oracle for W47 null runner, synthetic observations ONLY.

A block with word multiplicities c_i and n positions has expectation for
exact repeats at any fixed ordered distinct positions:
  p = sum_i(c_i*(c_i-1))/(n*(n-1)).
This is not substituted for the FROZEN Monte-Carlo scientific endpoint.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]

def load(path):
    spec=importlib.util.spec_from_file_location("w47_runner_oracle_target",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def exact_null_expectation(blocks):
    result=0.0
    for _,words,edges in blocks:
        n=len(words)
        if not edges:continue
        if n<2:raise ValueError("Ill-defined synthetic block")
        c=Counter(words)
        result+=len(edges)*sum(x*(x-1) for x in c.values())/(n*(n-1))
    return result

def audit(runner):
    many=[(f"fictional_{i}",("a","b","a","c","b"),((0,1),(1,2),(2,3),(3,4))) for i in range(25)]
    value=runner.null_counts(many,reps=10000,seed=20261116)
    oracle=exact_null_expectation(many)
    if abs(value["expected"]-oracle)>0.5:
        raise RuntimeError("Monte Carlo expectation diverges from independent exact oracle")
    if value["pairs"]!=100 or value["observed"]!=0 or len(value["observed_by_folio"])!=25:
        raise RuntimeError("Incorrect repeat count, edges or folio cluster count")
    if runner.bootstrap(value,reps=400,seed=20261116)!=[0.0,0.0]:
        raise RuntimeError("Folio bootstrap on zero-repeat fixture must be identically zero")
    repeated=[(f"fictional_{i}",("a","a","a"),((0,1),(1,2))) for i in range(25)]
    invariant=runner.null_counts(repeated,reps=100,seed=20261116)
    if (invariant["observed"],invariant["expected"],invariant["OE"],invariant["p_depletion"])!=(50,50,1,1):
        raise RuntimeError("Permutation-invariant equal-word negative control changed")
    if runner.bootstrap(invariant,reps=300)!=[1.0,1.0]:
        raise RuntimeError("Invariant folio CI must be one")
    none=[("fictional_one",("a","a"),())]
    try:
        runner.null_counts(none,reps=5)
        raise RuntimeError("Pairless block improperly accepted")
    except ValueError:
        pass
    support=dict(OE=0,p_depletion=0.001,CI95=[0,0.5],physical_folios=25)
    falsify=dict(OE=0.9,p_depletion=0.8,CI95=[0.6,1.3],physical_folios=25)
    if runner.synthetic_classify(support,support)!="SUPPORTED":
        raise RuntimeError("Incorrect SUPPORTED decision on synthetic known case")
    if runner.synthetic_classify(falsify,falsify)!="FALSIFIED":
        raise RuntimeError("Incorrect FALSIFIED decision on synthetic known case")
    if runner.synthetic_classify(support,falsify)!="INCONCLUSIVE":
        raise RuntimeError("Incorrect IT2a/ZL3b discordance decision")
    return {
      "status":"PASS_SYNTHETIC_INDEPENDENT_ORACLE",
      "classification":"TECHNICAL_RUNNER_CHECK_NO_SCIENTIFIC_DATA",
      "analytical_null_expected":oracle,
      "monte_carlo_null_expected":value["expected"],
      "synthetic_pairs":100,
      "synthetic_folio_clusters":25,
      "frozen_endpoint_modified":False,
      "scientific_analysis_executed":False,
      "holdout_file_read":False,
      "identifiers_exported":False,
      "limitations":["No empirical Voynich endpoint tested","No human-independent code review",
                     "Analytic check of Monte Carlo expectation does not certify isolation/partition provenance"]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--runner",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    report=audit(load(args.runner))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({key:report[key] for key in (
        "status","classification","scientific_analysis_executed","synthetic_pairs",
        "analytical_null_expected","monte_carlo_null_expected")},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("RUNNER ORACLE FAIL CLOSED:",type(exc).__name__,file=sys.stderr)
        sys.exit(1)
