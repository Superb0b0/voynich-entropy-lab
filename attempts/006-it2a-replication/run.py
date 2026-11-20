#!/usr/bin/env python3
"""Attempt 005/006 - refractory first-word-class model with a qo-specific parameter.
Reads ONLY $VOYNICH_DATA_DIR/<corpus file> (training-only filtered corpus). Writes results_ci.json in cwd.
Usage: python3 run.py ZL3b-n.txt   (or IT2a-n.txt for the replication attempt)
Deterministic: uses only random.Random(seed).random(); no set-order or hash-order dependence."""
import os,re,sys,json,math,random,hashlib,collections
DATA=os.environ.get('VOYNICH_DATA_DIR'); SEED=int(os.environ.get('VOYNICH_SEED','20261121'))
if not DATA: sys.exit('VOYNICH_DATA_DIR missing: fail closed')
FILE=sys.argv[1] if len(sys.argv)>1 else 'ZL3b-n.txt'
BURN,THIN,R_PRED,R_FIT=10,3,200,30            # FROZEN (see PROTOCOL.md)
GRID_T=[0.5*i for i in range(7)]; GRID_P=[0.5*i for i in range(9)]
CL=['qo','ch','sh','d','o','y','s']           # class 0=qo ... 7=other, order = priority of prefix match
raw=open(os.path.join(DATA,FILE),'rb').read()
rows=collections.defaultdict(list);page='';leaf=0;para=0
for line in raw.decode().splitlines():
 m=re.match(r'^<(f\d+[rv]\d*)>',line)
 if m:page=m[1];leaf=int(re.match(r'f(\d+)',page)[1]);para=0;continue
 m=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)',line)
 if not m or m[1]!=page:continue
 n,loc,s=int(m[2]),m[3],m[4]
 if 'P' not in loc:continue
 if '*P' in loc or '@P' in loc:para+=1
 s=re.sub(r'<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]','',s)
 tok=[re.sub(r'[^a-z]','',t.lower()) for t in re.split(r'[.,\s]+',s.strip())]
 tok=[t for t in tok if t]
 if tok:rows[(leaf,page,para)].append((n,tok[0]))
def cls(w):
 for i,c in enumerate(CL):
  if w.startswith(c):return i
 return 7
groups={0:[],1:[]}
for key in sorted(rows):
 leaf,page,para=key;rr=sorted(rows[key])
 sp=int(hashlib.sha256((str(leaf)+':20261114').encode()).hexdigest(),16)%2
 valid=[rr[i+1][0]==rr[i][0]+1 for i in range(len(rr)-1)]
 if sum(valid)<1:continue
 w=[r[1] for r in rr];groups[sp].append((w,[cls(x) for x in w],valid))
def stats(w,c,valid,idx):
 sn=qq=rp=0
 for p,v in enumerate(valid):
  if v:
   a,b=idx[p],idx[p+1]
   if c[a]==c[b]:
    if c[a]==0:qq+=1
    else:sn+=1
   if w[a]==w[b]:rp+=1
 return sn,qq,rp
def observed(sp):
 t=[0,0,0]
 for w,c,v in groups[sp]:
  s=stats(w,c,v,list(range(len(w))))
  for k in range(3):t[k]+=s[k]
 return t
def sample(sp,theta,phi,R,rng):
 wt=[theta+phi]+[theta]*7
 out=[[0,0,0] for _ in range(R)]
 for w,c,valid in groups[sp]:
  n=len(w);idx=list(range(n));last=n-2
  for i in range(n-1,0,-1):
   j=int(rng.random()*(i+1));idx[i],idx[j]=idx[j],idx[i]
  def pe(p):
   if 0<=p<=last and valid[p]:
    x=c[idx[p]]
    if x==c[idx[p+1]]:return wt[x]
   return 0.0
  def step(k):
   for _ in range(k):
    a=int(rng.random()*n);b=int(rng.random()*(n-1))
    if b>=a:b+=1
    ps=sorted({a-1,a,b-1,b});e0=sum(pe(p) for p in ps)
    idx[a],idx[b]=idx[b],idx[a]
    d=sum(pe(p) for p in ps)-e0
    if d<=0 or rng.random()<math.exp(-d):continue
    idx[a],idx[b]=idx[b],idx[a]
  step(BURN*n)
  for r in range(R):
   step(THIN*n);s=stats(w,c,valid,idx)
   o=out[r]
   for k in range(3):o[k]+=s[k]
 return out
def mean(sm,k):return sum(x[k] for x in sm)/len(sm)
def solve(grid,means,target):          # means decreasing in parameter; linear interpolation, clamped to grid
 if target>=means[0]:return grid[0]
 for i in range(len(grid)-1):
  a,b=means[i],means[i+1]
  if a>=target>=b:return grid[i] if a==b else grid[i]+(grid[i+1]-grid[i])*(a-target)/(a-b)
 return grid[-1]
def interval(sp,theta,phi,rng,ob):
 sm=sample(sp,theta,phi,R_PRED,rng);res={}
 for k,name in enumerate(['same_nonqo','qoqo','repeat']):
  v=sorted(x[k] for x in sm);lo=v[int(0.025*R_PRED)];hi=v[math.ceil(0.975*R_PRED)-1]
  res[name]=dict(observed=ob[k],mean=round(sum(v)/len(v),6),lo=lo,hi=hi,inside=bool(lo<=ob[k]<=hi))
 return res
rng=random.Random(SEED);result=dict(corpus=FILE,data_sha256=hashlib.sha256(raw).hexdigest(),seed=SEED,
 settings=dict(burn=BURN,thin=THIN,r_pred=R_PRED,r_fit=R_FIT,grid_theta=GRID_T,grid_phi=GRID_P,classes=CL+['other']),
 groups={str(s):dict(n_groups=len(groups[s]),valid_pairs=sum(sum(v) for _,_,v in groups[s])) for s in (0,1)},directions={})
for fit,pred in [(0,1),(1,0)]:
 of=observed(fit);op=observed(pred)
 sims=[sample(fit,t,0.0,R_FIT,rng) for t in GRID_T]
 th_nq=solve(GRID_T,[mean(s,0) for s in sims],of[0])
 th_all=solve(GRID_T,[mean(s,0)+mean(s,1) for s in sims],of[0]+of[1])
 simp=[sample(fit,th_nq,p,R_FIT,rng) for p in GRID_P]
 phi=solve(GRID_P,[mean(s,1) for s in simp],of[1])
 m2=interval(pred,th_nq,phi,rng,op);m1=interval(pred,th_all,0.0,rng,op)
 result['directions'][f'fit{fit}_pred{pred}']=dict(observed_fit=dict(zip(['same_nonqo','qoqo','repeat'],of)),
  theta_nonqo=round(th_nq,6),phi=round(phi,6),theta_all=round(th_all,6),M2_theta_phi=m2,M1_theta_only=m1)
d=result['directions'].values()
result['criteria']=dict(M2_all_inside_both_directions=all(m['inside'] for x in d for m in x['M2_theta_phi'].values()),
 M1_qoqo_excluded_both_directions=all(not x['M1_theta_only']['qoqo']['inside'] for x in d))
result['criteria']['verdict']='SUPPORTED' if all(result['criteria'].values()) else 'NOT SUPPORTED'
json.dump(result,open('results_ci.json','w'),indent=1,sort_keys=True)
print(json.dumps(result['criteria']),flush=True)
