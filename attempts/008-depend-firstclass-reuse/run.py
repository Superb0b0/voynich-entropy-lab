#!/usr/bin/env python3
"""Attempt 008 - VOY-DEPEND-01. Reads ONLY $VOYNICH_DATA_DIR/ZL3b-n.txt (training-only). Writes results_ci.json. Deterministic (random.Random.random only)."""
import os,re,sys,json,math,random,hashlib,collections
DATA=os.environ.get('VOYNICH_DATA_DIR');SEED=int(os.environ.get('VOYNICH_SEED','20261122'))
if not DATA: sys.exit('VOYNICH_DATA_DIR missing: fail closed')
EXPECTED='dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9'
R_MAIN,R_CAL,N_CAL,PLANT_Q=1999,199,60,0.25
raw=open(os.path.join(DATA,'ZL3b-n.txt'),'rb').read()
if hashlib.sha256(raw).hexdigest()!=EXPECTED: sys.exit('training-only corpus hash mismatch: fail closed')
CL=['qo','ch','sh','d','o','y','s']
def cls(w):
 for i,c in enumerate(CL):
  if w.startswith(c):return i
 return 7
def toks(s,variant):
 if variant=='B':s=re.sub(r'\[([^\]:]*):[^\]]*\]',r'\1',s)
 s=re.sub(r'<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]','',s)
 t=[re.sub(r'[^a-z]','',x.lower()) for x in re.split(r'[.,\s]+',s.strip())]
 return [x for x in t if x]
def parse(variant):
 rows=collections.defaultdict(list);page='';leaf=0;para=0
 for line in raw.decode().splitlines():
  m=re.match(r'^<(f\d+[rv]\d*)>',line)
  if m:page=m[1];leaf=int(re.match(r'f(\d+)',page)[1]);para=0;continue
  m=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)',line)
  if not m or m[1]!=page:continue
  n,loc,s=int(m[2]),m[3],m[4]
  if 'P' not in loc:continue
  if '*P' in loc or '@P' in loc:para+=1
  t=toks(s,variant)
  if t:rows[(leaf,page,para)].append((n,t))
 out={0:[],1:[]}
 for key in sorted(rows):
  leaf=key[0];rr=sorted(rows[key]);sp=int(hashlib.sha256((str(leaf)+':20261114').encode()).hexdigest(),16)%2
  out[sp].append(dict(leaf=leaf,nums=[r[0] for r in rr],heads=[r[1][0] for r in rr],bodies=[r[1][1:] for r in rr]))
 return out
def bucket(n):return 0 if n<=3 else (1 if n<=6 else 2)
class P:
 def __init__(s,d,mode):
  s.leaf=d['leaf'];m=len(d['heads']);s.cls=[cls(h) for h in d['heads']];s.bodies=d['bodies']
  s.lo,s.hi=(1,m-1) if mode=='interior' else (0,m)
  s.pidx=[]
  for p in range(m-1):
   if d['nums'][p+1]!=d['nums'][p]+1:continue
   if not d['bodies'][p] or not d['bodies'][p+1]:continue
   if mode=='interior' and not (p>=1 and p+1<=m-2):continue
   s.pidx.append(p)
  s.compute()
 def compute(s):
  s.pairs=[]
  for p in s.pidx:
   a=set(s.bodies[p]);b=s.bodies[p+1]
   y=sum(1 for t in b if t in a)/len(b)
   s.pairs.append((p,y,3*bucket(len(b))+bucket(len(s.bodies[p]))))
def stat(paras,cl):
 sy1=[0.0]*9;n1=[0]*9;sy0=[0.0]*9;n0=[0]*9;t1=0;a1=0.0;a0=0.0;m0=0
 for para,c in zip(paras,cl):
  for p,y,cell in para.pairs:
   if c[p]==c[p+1]:sy1[cell]+=y;n1[cell]+=1;t1+=1;a1+=y
   else:sy0[cell]+=y;n0[cell]+=1;a0+=y;m0+=1
 num=den=0.0
 for k in range(9):
  if n1[k] and n0[k]:num+=n1[k]*(sy1[k]/n1[k]-sy0[k]/n0[k]);den+=n1[k]
 sadj=num/den if den else 0.0
 mean0=a0/m0 if m0 else 0.0
 sraw=(a1/t1-a0/m0) if t1 and m0 else 0.0
 return sadj,sraw,t1,mean0
def perm_cls(para,rng):
 c=para.cls[:];lo,hi=para.lo,para.hi
 for i in range(hi-1,lo,-1):
  j=lo+int(rng.random()*(i-lo+1));c[i],c[j]=c[j],c[i]
 return c
def ptest(paras,obs_cls,R,rng):
 s0=stat(paras,obs_cls)[0];cnt=0
 for _ in range(R):
  if abs(stat(paras,[perm_cls(p,rng) for p in paras])[0])>=abs(s0)-1e-12:cnt+=1
 return s0,(cnt+1)/(R+1)
def analyse(paras,rng,R):
 paras=[p for p in paras if p.pairs]
 obs=[p.cls for p in paras];sadj,sraw,n1,m0=stat(paras,obs);_,pv=ptest(paras,obs,R,rng)
 leaves=sorted({p.leaf for p in paras});same=0
 for lf in leaves:
  keep=[p for p in paras if p.leaf!=lf];s=stat(keep,[p.cls for p in keep])[0]
  if s*sadj>0:same+=1
 return dict(n_pairs=sum(len(p.pairs) for p in paras),n_x1=n1,mean_y_x0=round(m0,6),s_adj=round(sadj,6),s_raw=round(sraw,6),rel_effect=round(sadj/m0,6) if m0 else None,p_two_sided=round(pv,6),loo_folio_same_sign=round(same/len(leaves),6),n_folios=len(leaves))
def plant(paras,rng):
 out=[]
 for p in paras:
  q=P.__new__(P);q.__dict__.update(p.__dict__);q.bodies=[b[:] for b in p.bodies]
  for pi in p.pidx:
   if p.cls[pi]==p.cls[pi+1] and rng.random()<PLANT_Q:
    src=q.bodies[pi];q.bodies[pi+1][int(rng.random()*len(q.bodies[pi+1]))]=src[int(rng.random()*len(src))]
  q.compute();out.append(q)
 return out
rng=random.Random(SEED);res=dict(seed=SEED,data_sha256=EXPECTED,settings=dict(r_main=R_MAIN,r_cal=R_CAL,n_cal=N_CAL,plant_q=PLANT_Q),splits={})
A=parse('A');B=parse('B')
for sp in (0,1):
 prim=[P(d,'interior') for d in A[sp]];prim=[p for p in prim if p.pairs]
 allp=[P(d,'all') for d in A[sp]];varB=[P(d,'interior') for d in B[sp]]
 r=dict(primary=analyse(prim,rng,R_MAIN),all_pairs_descriptive=analyse(allp,rng,R_MAIN),parser_B_descriptive=analyse(varB,rng,R_MAIN))
 qq=sum(1 for p in prim for q,_,_ in p.pairs if p.cls[q]==0 and p.cls[q+1]==0);r['qo_qo_interior_pairs']=qq
 rej_size=rej_pow=0
 for _ in range(N_CAL):
  sim=[perm_cls(p,rng) for p in prim];s0=stat(prim,sim)[0];cnt=0
  for _ in range(R_CAL):
   if abs(stat(prim,[perm_cls(p,rng) for p in prim])[0])>=abs(s0)-1e-12:cnt+=1
  rej_size+=((cnt+1)/(R_CAL+1)<=0.025)
  pl=plant(prim,rng);_,pv=ptest(pl,[p.cls for p in pl],R_CAL,rng);rej_pow+=(pv<=0.025)
 r['calibration']=dict(size_rate=round(rej_size/N_CAL,6),power_rate=round(rej_pow/N_CAL,6))
 res['splits'][str(sp)]=r
cal_ok=all(res['splits'][k]['calibration']['size_rate']<=0.07 and res['splits'][k]['calibration']['power_rate']>=0.60 for k in '01')
enough=all(res['splits'][k]['primary']['n_x1']>=30 for k in '01')
prim=[res['splits'][k]['primary'] for k in '01']
ok=all(x['p_two_sided']<=0.025 and abs(x['rel_effect'])>=0.15 for x in prim) and prim[0]['s_adj']*prim[1]['s_adj']>0
res['criteria']=dict(calibration_ok=cal_ok,numerosity_ok=enough,verdict='NON INTERPRETABILE' if not cal_ok else ('NON VALUTABILE' if not enough else ('SUPPORTED' if ok else 'NOT SUPPORTED')))
json.dump(res,open('results_ci.json','w'),indent=1,sort_keys=True);print(json.dumps(res['criteria']))
