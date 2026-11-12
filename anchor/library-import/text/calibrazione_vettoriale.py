import numpy as np, random, json, hashlib, importlib.util, re
from pathlib import Path
P=Path('/mnt/data/files/ANCHOR02_test_v1_1.py'); C=Path('/mnt/data/files/ZL3b-n(9).txt')
spec=importlib.util.spec_from_file_location('v11',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=random.Random(20261112); NR=20000
rings={'A':[(i+1,f'A{i+1}') for i in range(14)],'B':[(i+1,f'B{i+1}') for i in range(15)]}
keys=[f for arr in rings.values() for _,f in arr]

def generate(effect):
  excluded=set(R.sample(keys,R.randint(0,4))); b={}
  for ring in ('A','B'):
    prev=None
    for _,f in rings[ring]:
      if effect and prev is not None and R.random()<.70:g=prev
      else:g=R.randrange(6)
      prev=g
      if f not in excluded:b[f]=('alta',g)
  return b

def fastcalc(b,seed):
  rng=np.random.default_rng(seed)
  obs=0; sim=np.zeros(NR,dtype=np.int16); ed=0
  for ring in ('A','B'):
    fs=[f for _,f in rings[ring]];included=[f for f in fs if f in b]
    vals=np.asarray([b[f][1] for f in included],dtype=np.int8)
    idx={f:i for i,f in enumerate(included)}
    edges=[(idx[a],idx[c]) for a,c in zip(fs,fs[1:]+fs[:1]) if a in idx and c in idx]
    ed+=len(edges)
    obs+=sum(vals[i]==vals[j] for i,j in edges)
    matrix=np.broadcast_to(vals,(NR,len(vals))).copy()
    matrix=rng.permuted(matrix,axis=1)
    for i,j in edges:sim+=matrix[:,i]==matrix[:,j]
  mu=float(sim.mean());p=(1+int(np.count_nonzero(np.abs(sim-mu)>=abs(obs-mu)-1e-12)))/(NR+1)
  return len(b),ed,obs,mu,p

out={}; examples=[]
for label,n,effect in [('null',500,False),('planted',200,True)]:
  positive=0;ps=[];edges=[];ns=[]
  for k in range(n):
    b=generate(effect);v=fastcalc(b,20261113+k+(0 if not effect else 100000));positive+=v[-1]<.05;ps.append(v[-1]);edges.append(v[1]);ns.append(v[0]);
    if k<2:examples.append([label,k, v, m.calc(rings,b,{'alta'},m.SEED)[-1]])
  out[label]={'datasets':n,'positives':positive,'fraction':positive/n,'n_min_max':[min(ns),max(ns)],'pairs_min_max':[min(edges),max(edges)],'p_min_max':[min(ps),max(ps)]}
  print(label,out[label],flush=True)
out['seed_synthetic']=20261112;out['seed_vectorized_permutations_start']=20261113;out['examples_p_fast_vs_original_script']=examples
out['note']='Synthetic data only. Equivalent statistic, thresholds and p calculation; numpy vectorized permutation RNG differs from Python random.Random of frozen script. Original script used for 4 cross-checks.'
Path('/mnt/data/calibrazione_pre_freeze.json').write_text(json.dumps(out,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x))+'\n')
# B no images no join
lines=[]
for line in C.read_text().splitlines():
 mm=re.match(r'^<(f70v2\.\d+),([^>]*)>\s+(.*)$',line)
 if mm and re.search(r'[@&]L',mm.group(2)):
  raw=mm.group(3).strip();g=m.first_glyph(raw)
  reason='esclusa: stella centrale secondo protocollo (identificazione visiva NON validata)' if mm.group(1)=='f70v2.33' else ('esclusa: carattere incerto ?' if '?' in raw else ('esclusa: alternativa [...]' if re.search(r'\[[^\]]*:[^\]]*\]',raw) else ('ammissibile testualmente; annotazione interna {…} rimossa dallo script' if '{' in raw else 'ammissibile testualmente')))
  lines.append({'id':mm.group(1),'forma_EVA':raw,'glifo_v11':g,'esito':reason})
Path('/mnt/data/f70v2_glifi_pre_freeze.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2)+'\n')
print('B',len(lines), 'excluded',sum('esclusa' in v['esito'] for v in lines))