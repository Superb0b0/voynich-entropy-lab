import re,random,hashlib,json,collections
raw=open('data/ZL3b-n.txt','rb').read()
assert hashlib.sha256(raw).hexdigest()=='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
held={2,5,9,17,31,32,36,37,38,45,48,49,67,69,78,85,86,94,95,101,111}
rows=collections.defaultdict(list);page='';leaf=0;para=0
for line in raw.decode().splitlines():
 m=re.match(r'^<(f\d+[rv]\d*)>',line)
 if m:page=m[1];leaf=int(re.match(r'f(\d+)',page)[1]);para=0;continue
 m=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)',line)
 if not m or leaf in held or m[1]!=page:continue
 n,loc,s=int(m[2]),m[3],m[4]
 if 'P' not in loc:continue
 if '*P' in loc or '@P' in loc:para+=1
 s=re.sub(r'<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]','',s)
 tok=re.split(r'[.,\s]+',s.strip())
 tok=[re.sub(r'[^a-z]','',t.lower()) for t in tok]
 tok=[t for t in tok if t]
 if tok:rows[(leaf,page,para)].append((n,tok[0],len(tok)))
def calc(mode,minimum=1,within_para=True,seed=20261114):
 groups=collections.defaultdict(list)
 for (leaf,page,para),rr in rows.items():
  split=int(hashlib.sha256((str(leaf)+':20261114').encode()).hexdigest(),16)%2
  key=(split,leaf,page,para if within_para else 0)
  groups[key].extend(rr)
 out=[]
 for split in [0,1]:
  gr=[sorted(v) for k,v in groups.items() if k[0]==split]
  def stat(shuffle=False,rng=None):
   hit=den=0
   for g in gr:
    gg=[r for r in g if r[2]>=minimum]
    if len(gg)<2:continue
    words=[r[1] for r in gg]
    if shuffle:rng.shuffle(words)
    for i in range(len(gg)-1):
     if gg[i+1][0]!=gg[i][0]+1:continue
     a,b=words[i],words[i+1]
     if mode=='repeat':den+=1;hit+=a==b
     else:
      if a.startswith('qo'):den+=1;hit+=b.startswith('qo')
   return hit,den
  observed,den=stat()
  rng=random.Random(seed+split)
  null=[stat(True,rng)[0] for _ in range(1000)]
  mean=sum(null)/len(null);p=(1+sum(v<=observed for v in null))/1001
  out.append(dict(split=split,observed=observed,denominator=den,null_mean=mean,ratio=observed/mean if mean else None,p_one_sided=p,null_95=[sorted(null)[25],sorted(null)[974]],folios=len({k[1] for k in groups if k[0]==split})))
 return out
result={'data_sha256':hashlib.sha256(raw).hexdigest(),'protocol_sha256':'e6f7c3c369bbf86ccd92723f9310f952a8f8272f8f686301a78695d22e54aaaa','groups':len(rows),'tests':{}}
for mode in ['repeat','qo']:
 result['tests'][mode]={'primary':calc(mode,seed=20261114 if mode=='repeat' else 20261115),'page_null':calc(mode,within_para=False,seed=20261116),'long_lines':calc(mode,minimum=5,seed=20261117)}
print(json.dumps(result,indent=2))
