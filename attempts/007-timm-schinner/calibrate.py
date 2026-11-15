#!/usr/bin/env python3
"""Pre-registered gate for attempt 007; calibration only. No Timm-Schinner inputs."""
import ast, collections, hashlib, json, math, os, pathlib, random, re
src=pathlib.Path("attempts/005-refractory-qo-parameter/run.py").read_text()
tree=ast.parse(src)
# Reuse the EXACT parsing, class and sampling functions from 005; exclude its experiment runner.
cut=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="rng" for t in n.targets))
env={"__name__":"__calibration__"}
exec(compile(ast.Module(body=tree.body[:cut],type_ignores=[]),"attempt005","exec"),env)
groups=env["groups"]; sample=env["sample"]; mean=env["mean"]; solve=env["solve"]
GRID_T=env["GRID_T"];GRID_P=env["GRID_P"]
# Synthesize a reordered word sequence using EXACT 005 Metropolis swap energy.
def synth_group(w,c,valid,theta,phi,rng):
 n=len(w);idx=list(range(n));wt=[theta+phi]+[theta]*7
 for i in range(n-1,0,-1):
  j=int(rng.random()*(i+1));idx[i],idx[j]=idx[j],idx[i]
 def pe(p):
  if 0<=p<n-1 and valid[p]:
   x=c[idx[p]]
   if x==c[idx[p+1]]:return wt[x]
  return 0.0
 for _ in range(50*n):
  a=int(rng.random()*n);b=int(rng.random()*(n-1))
  if b>=a:b+=1
  ps=sorted({a-1,a,b-1,b});e0=sum(pe(p) for p in ps)
  idx[a],idx[b]=idx[b],idx[a]
  d=sum(pe(p) for p in ps)-e0
  if d>0 and rng.random()>=math.exp(-d):idx[a],idx[b]=idx[b],idx[a]
 return [w[i] for i in idx],[c[i] for i in idx],valid
original=groups
results=[]
for seed in range(1,6):
 rng=random.Random(seed)
 groups[0]=[synth_group(w,c,v,0.8,1.2,rng) for w,c,v in original[0]]
 of=[0,0,0]
 for w,c,v in groups[0]:
  s=env["stats"](w,c,v,list(range(len(w))))
  of=[a+b for a,b in zip(of,s)]
 fitrng=random.Random(10000+seed)
 sims=[sample(0,t,0.0,env["R_FIT"],fitrng) for t in GRID_T]
 theta=solve(GRID_T,[mean(s,0) for s in sims],of[0])
 simp=[sample(0,theta,p,env["R_FIT"],fitrng) for p in GRID_P]
 phi=solve(GRID_P,[mean(s,1) for s in simp],of[1])
 passed=0.5<=theta<=1.1 and 0.7<=phi<=1.7
 results.append(dict(seed=seed,theta=round(theta,6),phi=round(phi,6),pass_gate=passed,observed=of))
 groups[0]=original[0]
report=dict(gate="007-calibration",known_theta=0.8,known_phi=1.2,replications=results,passed=sum(x["pass_gate"] for x in results),required=4)
report["verdict"]="PASS" if report["passed"]>=4 else "STOP"
pathlib.Path("calibration_007.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2),flush=True)
if report["verdict"]!="PASS":raise SystemExit(1)
