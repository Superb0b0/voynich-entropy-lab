#!/usr/bin/env python3
"""CAL-01 synthetic recovery: no Voynich corpus, no holdout access."""
import hashlib,json,random,statistics
SEED=20261113
N_REPS=400
N_GROUPS=120
GROUP_SIZE=8
ALPHA=0.01
# Pre-registered: distinguish iid Bernoulli(0.35) from a first-order
# anti-persistence generator with P(1|1)=0.08 and P(1|0)=0.50.
# Statistic: P(1|1)-P(1|0), negative for anti-persistence.
# Threshold: 1% lower quantile of independent iid calibration sample.
# Success criterion: false-positive rate <= 0.025 and power >= 0.80
# on independent batches; calibration and evaluation seeds separated.
def simulate(seed,kind):
 r=random.Random(seed); groups=[]
 for _ in range(N_GROUPS):
  g=[int(r.random()<0.35)]
  for i in range(GROUP_SIZE-1):
   p=0.35 if kind=='iid' else (0.08 if g[-1] else 0.50)
   g.append(int(r.random()<p))
  groups.append(g)
 return groups
def stat(gs):
 a=b=c=d=0
 for g in gs:
  for x,y in zip(g,g[1:]):
   if x:a+=y;b+=1
   else:c+=y;d+=1
 return a/b-c/d if b and d else None
null=sorted(stat(simulate(SEED+100000+i,'iid')) for i in range(N_REPS))
threshold=null[max(0,int(ALPHA*N_REPS)-1)]
results={}
for kind in ('iid','anti'):
 vals=[stat(simulate(SEED+200000+i+(0 if kind=='iid' else 10000),kind)) for i in range(N_REPS)]
 results[kind]={'mean_stat':round(statistics.mean(vals),6),'positive_count':sum(v<=threshold for v in vals),'rate':round(sum(v<=threshold for v in vals)/N_REPS,6)}
report={'status':'SYNTHETIC_CALIBRATION_ONLY','seed':SEED,'replicates_per_family':N_REPS,'groups':N_GROUPS,'group_size':GROUP_SIZE,'alpha':ALPHA,'threshold':threshold,'results':results,'criteria':{'false_positive_max':0.025,'power_min':0.80},'pass':results['iid']['rate']<=0.025 and results['anti']['rate']>=0.80,'limitations':['synthetic generators only; not ms408/Naibbe/Timm-Schinner','no Voynich text accessed','no folio holdout opened','not a qualifying attempt']}
print(json.dumps(report,indent=2,sort_keys=True))
