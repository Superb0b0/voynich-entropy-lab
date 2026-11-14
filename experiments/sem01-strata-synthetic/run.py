import random,json,hashlib,pathlib
R=random.Random(20261114)
rows=[]
for s in (0,1):
 for f in range(40):
  p=.15 if s==0 else .85
  x=int(R.random()<p);y=int(R.random()<p)
  rows.append((s,x,y))
def phi(items):
 n=len(items); mx=sum(x for _,x,y in items)/n;my=sum(y for _,x,y in items)/n
 vx=mx*(1-mx);vy=my*(1-my)
 return sum((x-mx)*(y-my) for _,x,y in items)/n/(vx*vy)**.5 if vx*vy else 0
def conditional(items):
 return sum(phi([r for r in items if r[0]==s])*sum(r[0]==s for r in items)/len(items) for s in (0,1))
obs=phi(rows);cond=conditional(rows);pooled=0;strat=0
for i in range(2000):
 labels=[r[2] for r in rows];R.shuffle(labels)
 rp=[(s,x,labels[j]) for j,(s,x,y) in enumerate(rows)]
 pooled+=abs(phi(rp))>=abs(obs)
 labels=[r[2] for r in rows]
 for s in (0,1):
  indices=[j for j,r in enumerate(rows) if r[0]==s]
  vals=[labels[j] for j in indices];R.shuffle(vals)
  for j,v in zip(indices,vals):labels[j]=v
 rs=[(s,x,labels[j]) for j,(s,x,y) in enumerate(rows)]
 strat+=abs(conditional(rs))>=abs(cond)
result={'protocol_sha256':hashlib.sha256(pathlib.Path(__file__).with_name('protocol.txt').read_bytes()).hexdigest(),'seed':20261114,'folios':80,'per_section':40,'draws':2000,'pooled_phi':round(obs,6),'conditional_phi':round(cond,6),'pooled_permutation_p':round((pooled+1)/2001,6),'stratified_permutation_p':round((strat+1)/2001,6),'status':'SYNTHETIC_ONLY'}
print(json.dumps(result,sort_keys=True,indent=2))
