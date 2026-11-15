#!/usr/bin/env python3
"""013: two-parameter soft-spacing rival, trained on ZL3b only."""
import ast,hashlib,json,math,os,pathlib,random,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA=pathlib.Path(os.environ.get("VOYNICH_DATA_DIR","/nonexistent"))
HASH={"ZL3b-n.txt":"dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9","IT2a-n.txt":"a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c"}
for name,sha in HASH.items():
 path=DATA/name
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:sys.exit("FAIL CLOSED: training-only hash "+name)
def load(name):
 os.environ["VOYNICH_SEED"]="20261121"
 sys.argv=["run.py",name]
 path=ROOT/"attempts/005-refractory-qo-parameter/run.py"
 tree=ast.parse(path.read_text())
 cut=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="rng" for t in n.targets))
 env={"__name__":"__013__"}
 exec(compile(ast.Module(body=tree.body[:cut],type_ignores=[]),str(path),"exec"),env)
 return env["groups"]
zl=load("ZL3b-n.txt");it=load("IT2a-n.txt")
def stats(w,c,v,idx):
 same=qq=repeat=triples=lag2=qo2=0
 for i,ok in enumerate(v):
  if not ok:continue
  a,b=idx[i],idx[i+1]
  if c[a]==c[b]:
   same+=1
   if c[a]==0:qq+=1
  if w[a]==w[b]:repeat+=1
  if i+1<len(v) and v[i+1]:
   z=idx[i+2]
   if c[a]==c[b]==c[z]:triples+=1
   if c[a]==c[z]:lag2+=1
   if c[a]==0 and c[z]==0:qo2+=1
 return (same,qq,repeat,triples,lag2,qo2)
def obs(groups,sp):
 out=[0]*6
 for w,c,v in groups[sp]:
  for k,x in enumerate(stats(w,c,v,list(range(len(w))))):out[k]+=x
 return out
def simulate(groups,sp,theta,lam,R,seed,kind):
 rng=random.Random(seed);out=[[0]*6 for _ in range(R)]
 for w,c,v in groups[sp]:
  n=len(w);idx=list(range(n))
  for i in range(n-1,0,-1):
   j=int(rng.random()*(i+1));idx[i],idx[j]=idx[j],idx[i]
  def energy(p):
   e=0.
   if 0<=p<n-1 and v[p] and c[idx[p]]==c[idx[p+1]]:
    e+=theta
    if kind=="M2" and c[idx[p]]==0:e+=lam
   if kind=="S1" and 0<=p<n-2 and v[p] and v[p+1] and c[idx[p]]==0 and c[idx[p+2]]==0:e+=lam
   return e
  def step(k):
   for _ in range(k):
    a=int(rng.random()*n);b=int(rng.random()*(n-1))
    if b>=a:b+=1
    ps=sorted({a-2,a-1,a,b-2,b-1,b})
    old=sum(energy(p) for p in ps)
    idx[a],idx[b]=idx[b],idx[a]
    delta=sum(energy(p) for p in ps)-old
    if delta>0 and rng.random()>=math.exp(-delta):idx[a],idx[b]=idx[b],idx[a]
  step(10*n)
  for r in range(R):
   step(3*n)
   z=stats(w,c,v,idx)
   for k in range(6):out[r][k]+=z[k]
 return out
fitted=json.loads((ROOT/"attempts/005-refractory-qo-parameter/results.json").read_text())
result={"status":"EXPLORATORY","training_hashes":HASH,"directions":{},"fit_draws_per_grid":200,"prediction_draws":200}
T=[i*.25 for i in range(11)];L=[i*.25 for i in range(13)]
names=["same_all","qoqo","repeat","triple_windows_sameclass","lag2_sameclass","qo_distance2"]
for fit,pred in [(0,1),(1,0)]:
 key=f"fit{fit}_pred{pred}";target=obs(zl,fit)
 # Predeclared standardization: Poisson scale, fixed from observed training target.
 scale0=max(1,target[0]);scale5=max(1,target[5])
 best=None
 for ti,t in enumerate(T):
  for li,l in enumerate(L):
   draws=simulate(zl,fit,t,l,200,20261121+fit*100000+ti*1000+li,"S1")
   m0=sum(z[0] for z in draws)/200;m5=sum(z[5] for z in draws)/200
   loss=(m0-target[0])**2/scale0+(m5-target[5])**2/scale5
   if best is None or (loss,t,l)<best[:3]:best=(loss,t,l,m0,m5)
 _,theta,lam,m0,m5=best
 actual=obs(it,pred);models={}
 for model,t,l in [("M2",fitted["directions"][key]["theta_nonqo"],fitted["directions"][key]["phi"]),("S1",theta,lam)]:
  draws=simulate(it,pred,t,l,200,20261121+100*fit+pred,model)
  metrics={}
  for k,name in enumerate(names):
   a=sorted(z[k] for z in draws);lo,hi=a[5],a[194]
   metrics[name]={"observed":actual[k],"mean":round(sum(a)/200,4),"lo":lo,"hi":hi,"inside":lo<=actual[k]<=hi}
  models[model]={"theta":t,"lambda":l,"metrics":metrics}
 result["directions"][key]={"S1_training_fit":{"loss":round(best[0],6),"same_mean":m0,"qo_distance2_mean":m5},"models":models}
 print("Completed",key,flush=True)
def covers(model):
 return all(d["models"][model]["metrics"]["qoqo"]["inside"] for d in result["directions"].values())
result["verdict"]="S1_CHALLENGES_UNIQUENESS" if covers("S1") else ("M2_WINS_QO_ENDPOINT" if covers("M2") else "INCONCLUSIVE")
(ROOT/"results_ci_013.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"verdict":result["verdict"],"directions":result["directions"]},indent=2),flush=True)
