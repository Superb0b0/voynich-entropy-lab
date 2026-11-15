#!/usr/bin/env python3
"""Attempt 012: frozen M2 versus uniform minimum-qoqo spacing rival S0."""
import ast,hashlib,json,math,os,pathlib,random,re,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
safe=pathlib.Path(os.environ.get("VOYNICH_DATA_DIR","/nonexistent"))
source=safe/"IT2a-n.txt"
if not source.is_file():sys.exit("FAIL CLOSED: prepared training corpus missing")
digest=hashlib.sha256(source.read_bytes()).hexdigest()
expected="a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c"
if digest!=expected:sys.exit("FAIL CLOSED: training SHA mismatch "+digest)
os.environ["VOYNICH_SEED"]="20261121"
sys.argv=["run.py","IT2a-n.txt"]
if True:
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
  sn,qq,rp=env["stats"](w,c,v,idx)
  return sn,qq,rp,run3,lag2
 def observed(sp):
  out=[0,0,0,0,0]
  for w,c,v in groups[sp]:
   z=novel(w,c,v,list(range(len(w))))
   out=[a+b for a,b in zip(out,z)]
  return out
 def predict(sp,theta,phi,R,rng):
  wt=[theta+phi]+[theta]*7
  out=[[0,0,0,0,0] for _ in range(R)]
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
    for j in range(5):out[r][j]+=z[j]
  return out
 from functools import lru_cache
 def spacing(sp,R,rng):
  out=[[0,0,0,0,0] for _ in range(R)]
  for w,c,valid in groups[sp]:
   n=len(w);q=sum(x==0 for x in c)
   @lru_cache(None)
   def dp(i,left,prev):
    if i==n:return (0,1) if left==0 else (10**9,0)
    opts=[]
    for isq in (0,1):
     if isq>left or n-i-1<left-isq:continue
     cost,ways=dp(i+1,left-isq,isq)
     cost+=int(i>0 and valid[i-1] and prev and isq)
     opts.append((cost,ways,isq))
    best=min(z[0] for z in opts)
    return best,sum(z[1] for z in opts if z[0]==best)
   dp(0,q,0)
   qw=[i for i,x in enumerate(c) if x==0];other=[i for i,x in enumerate(c) if x!=0]
   for r in range(R):
    left=q;prev=0;mask=[]
    for i in range(n):
     best,ways=dp(i,left,prev)
     choices=[]
     for isq in (0,1):
      if isq>left or n-i-1<left-isq:continue
      cost,count=dp(i+1,left-isq,isq)
      if cost+int(i>0 and valid[i-1] and prev and isq)==best:choices.append((isq,count))
     pick=int(rng.random()*sum(count for _,count in choices))
     for isq,count in choices:
      if pick<count:break
      pick-=count
     mask.append(isq);left-=isq;prev=isq
    qa=qw[:];ot=other[:]
    for arr in (qa,ot):
     for i in range(len(arr)-1,0,-1):
      j=int(rng.random()*(i+1));arr[i],arr[j]=arr[j],arr[i]
    idx=[];qi=oi=0
    for isq in mask:
     if isq:idx.append(qa[qi]);qi+=1
     else:idx.append(ot[oi]);oi+=1
    z=novel(w,c,valid,idx)
    for k in range(5):out[r][k]+=z[k]
  return out
 fitted=json.loads((ROOT/"attempts/005-refractory-qo-parameter/results.json").read_text())
 result={"status":"EXPLORATORY","filtered_training_sha256":digest,"directions":{}}
 for fit,pred in [(0,1),(1,0)]:
  name=f"fit{fit}_pred{pred}"
  d=fitted["directions"][name]
  theta=d["theta_nonqo"];phi=d["phi"]
  rng=random.Random(20261121+100*fit+pred)
  obs=observed(pred)
  models={}
  for model,t,p in [("M2",theta,phi),("S0",None,None)]:
   rng=random.Random(20261121+100*fit+pred)
   sims=predict(pred,t,p,200,rng) if model=="M2" else spacing(pred,200,rng)
   metrics={}
   for k,key in enumerate(["same_nonqo","qoqo","repeat","triple_windows_sameclass","lag2_sameclass"]):
    v=sorted(row[k] for row in sims)
    lo,hi=v[5],v[194]
    metrics[key]={"observed":obs[k],"predicted_mean":round(sum(v)/len(v),5),"lo":lo,"hi":hi,"inside":lo<=obs[k]<=hi}
   models[model]={"theta":t,"phi":p,"metrics":metrics}
  result["directions"][name]=models
 result["S0_challenges_uniqueness"]=all(d["S0"]["metrics"]["qoqo"]["inside"] for d in result["directions"].values())
 result["M2_qoqo_inside"]=all(d["M2"]["metrics"]["qoqo"]["inside"] for d in result["directions"].values())
 result["verdict"]="S0_CHALLENGES_UNIQUENESS" if result["S0_challenges_uniqueness"] else ("M2_WINS_QO_ENDPOINT" if result["M2_qoqo_inside"] else "INCONCLUSIVE")
 print(json.dumps(result,indent=2),flush=True)
 (ROOT/"results_ci_012.json").write_text(json.dumps(result,indent=2)+"\n")
