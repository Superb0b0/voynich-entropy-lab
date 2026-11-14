#!/usr/bin/env python3
"""Technical fixture only. No Voynich data; not scientific evidence."""
import argparse,json,hashlib,random,pathlib
p=argparse.ArgumentParser()
p.add_argument("--seed",type=int,required=True)
p.add_argument("--output",required=True)
a=p.parse_args()
rng=random.Random(a.seed)
values=[rng.randrange(1000000) for _ in range(64)]
result={"count":len(values),"sum":sum(values),"sha256":hashlib.sha256(json.dumps(values,separators=(",",":")).encode()).hexdigest()}
pathlib.Path(a.output).write_text(json.dumps(result,sort_keys=True)+"\n")
