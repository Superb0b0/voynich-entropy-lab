import random,json,statistics
SEED=20261113
REPS=400; GROUPS=120; SIZE=8

def sample(seed,kind):
 r=random.Random(seed); out=[]
 for _ in range(GROUPS):
  if kind=='heterogeneous': p=r.choice([.08,.62])
  elif kind=='beta': p=r.betavariate(1.4,2.6)
  else:p=.35
  g=[int(r.random()<p)]
  for i in range(SIZE-1):
   if kind=='anti':q=.08 if g[-1] else .50
   elif kind=='persistent':q=.65 if g[-1] else .19
   elif kind=='drift':q=.12 if i<3 else .58
   else:q=p
   g.append(int(r.random()<q))
  out.append(g)
 return out

def stat(gs):
 a=b=c=d=0
 for g in gs:
  for x,y in zip(g,g[1:]):
   if x:a+=y;b+=1
   else:c+=y;d+=1
 return a/b-c/d
null=sorted(stat(sample(SEED+100000+i,'iid')) for i in range(REPS))
threshold=null[3]
res={}
for j,kind in enumerate(['iid','heterogeneous','beta','drift','anti','persistent']):
 v=[stat(sample(SEED+200000+j*10000+i,kind)) for i in range(REPS)]
 res[kind]={'mean':round(statistics.mean(v),6),'below_threshold':sum(x<=threshold for x in v),'rate':sum(x<=threshold for x in v)/REPS}
print(json.dumps({'seed':SEED,'threshold':threshold,'replicates':REPS,'status':'EXPLORATORY_STRESS_TEST','results':res,'interpretation':'A rejection in a null with group heterogeneity or drift is a confounding false positive, not evidence for a true sequential mechanism.'},indent=2,sort_keys=True))
