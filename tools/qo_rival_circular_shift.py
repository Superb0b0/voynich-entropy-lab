#!/usr/bin/env python3
"""QO-RIVAL-05: circular-shift null preserving within-paragraph order.
Exploratory, training-only, independent of the two shuffle baselines.
"""
import collections, hashlib, importlib.util, json, random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("qo_rival_calibration", ROOT/"tools/qo_rival_calibration.py")
qo=importlib.util.module_from_spec(spec)
spec.loader.exec_module(qo)
SEED=20261115
REPS=2000

def rotate_groups(groups,rng):
    out={}
    for key,records in groups.items():
        ordered=sorted(records)
        if not ordered:
            out[key]=[]
            continue
        offset=rng.randrange(len(ordered))
        words=[word for _,word in ordered]
        rotated=words[offset:]+words[:offset]
        out[key]=[(ordered[i][0],rotated[i]) for i in range(len(ordered))]
    return out

def main():
    groups=qo.parse()  # checks corpus SHA and excludes held-out leaves
    observed_n,observed_d=qo.count(groups)
    if not groups or observed_d==0:
        raise SystemExit("BLOCKED: empty groups or denominator")
    observed=observed_n/observed_d
    rng=random.Random(SEED)
    rates=[]
    for _ in range(REPS):
        n,d=qo.count(rotate_groups(groups,rng))
        if d==0:
            raise SystemExit("BLOCKED: zero denominator in null replicate")
        rates.append(n/d)
    rates.sort()
    result={
        "classification":"EXPLORATORY_NOT_VALIDATED",
        "corpus_sha256":qo.SHA,
        "heldout_excluded":True,
        "model":"independent random circular shift of first words within each page-paragraph",
        "note":"Preserves within-paragraph word order and qo clustering but relocates sequence relative to fixed locus boundaries; NOT an independent validation.",
        "seed":SEED,"replicates":REPS,
        "observed":{"numerator":observed_n,"denominator":observed_d,"rate":observed},
        "null":{"mean_rate":sum(rates)/len(rates),"interval_95":[rates[49],rates[1949]],
                "p_depletion":(1+sum(x<=observed for x in rates))/(REPS+1)}
    }
    out=ROOT/"research-output"
    out.mkdir(exist_ok=True)
    (out/"qo-rival-circular-shift.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
