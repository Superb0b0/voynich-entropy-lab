#!/usr/bin/env python3
"""Attempt 009: fixed-parameter M2 posterior predictive checks on unfitted metrics."""
import ast,hashlib,json,math,os,pathlib,random,re,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from verify_attempts import protected,sanitize
source=ROOT/"data/ZL3b-n.txt"
# Filter protected pages before loading any observations into the model.
with tempfile.TemporaryDirectory() as td:
 safe=pathlib.Path(td)
 (safe/"ZL3b-n.txt").write_text(sanitize(source.read_text(),protected()))
 digest=hashlib.sha256((safe/"ZL3b-n.txt").read_bytes()).hexdigest()
 expected="dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9"
 if digest!=expected:sys.exit("STOP: filtered training SHA mismatch "+digest)
 os.environ["VOYNICH_DATA_DIR"]=str(safe)
 os.environ["VOYNICH_SEED"]="20261121"
 path=ROOT/"attempts/005-refractory-qo-parameter/run.py"
 tree=ast.parse(path.read_text())
 cut=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="rng" for t in n.targets))
 env={"__name__":"__009__"}
 exec(compile(ast.Module(body=tree.body[:cut],type_ignores=[]),str(path),"exec"),env)
 groups=env["groups"]
 def novel(w,c,v,idx):
  run3=lag2=0
  for p in range(len(v)-1):
   if v[p] and v[p+1]:
    if c[idx[p]]==c[idx[p+1]]==c[idx[p+2]]:run3+=1
    if c[idx[p]]==c[idx[p+2]]:lag2+=1
  return run3,lag2
 def observed(sp):
  out=[0,0]
  for w,c,v in groups[sp]:
   z=novel(w,c,v,list(range(len(w))))
   out=[a+b for a,b in zip(out,z)]
  return out
 def predict(sp,theta,phi,R,rng):
  wt=[theta+phi]+[theta]*7
  out=[[0,0] for _ in range(R)]
  for w,c,valid in groups[sp]:
   n=len(w);idx=list(range(n))
   for i in range(n-1,0,-1):
    j=int(rng.random()*(i+1));idx[i],idx[j]=idx[j],idx[i]
   def pe(p):
    if 0<=p<n-1 and valid[p]:
     x=c[idx[p]]
     if x==c[idx[p+1]]:return wt[x]
    return 0.
   def step(k):
    for _ in range(k):
     a=int(rng.random()*n);b=int(rng.random()*(n-1))
     if b>=a:b+=1
     ps=sorted({a-1,a,b-1,b});old=sum(pe(p) for p in ps)
     idx[a],idx[b]=idx[b],idx[a]
     d=sum(pe(p) for p in ps)-old
     if d>0 and rng.random()>=math.exp(-d):idx[a],idx[b]=idx[b],idx[a]
   step(env["BURN"]*n)
   for r in range(R):
    step(env["THIN"]*n)
    z=novel(w,c,valid,idx)
    for j in range(2):out[r][j]+=z[j]
  return out
 fitted=json.loads((ROOT/"attempts/005-refractory-qo-parameter/results.json").read_text())
 result={"status":"EXPLORATORY","filtered_training_sha256":digest,"directions":{}}
 for fit,pred in [(0,1),(1,0)]:
  name=f"fit{fit}_pred{pred}"
  d=fitted["directions"][name]
  theta=d["theta_nonqo"];phi=d["phi"]
  rng=random.Random(20261121+100*fit+pred)
  sims=predict(pred,theta,phi,200,rng)
  obs=observed(pred)
  metrics={}
  for k,key in enumerate(["runs_sameclass_ge3","lag2_sameclass"]):
   v=sorted(row[k] for row in sims)
   lo,hi=v[5],v[194]
   metrics[key]={"observed":obs[k],"predicted_mean":round(sum(v)/len(v),5),"lo":lo,"hi":hi,"inside":lo<=obs[k]<=hi}
  result["directions"][name]={"theta":theta,"phi":phi,"metrics":metrics}
 result["all_inside"]=all(m["inside"] for d in result["directions"].values() for m in d["metrics"].values())
 result["verdict"]="M2_PASSES_NEW_CHECKS" if result["all_inside"] else "M2_FAILS_NEW_CHECKS"
 print(json.dumps(result,indent=2),flush=True)
 (ROOT/"results_ci_009.json").write_text(json.dumps(result,indent=2)+"\n")
