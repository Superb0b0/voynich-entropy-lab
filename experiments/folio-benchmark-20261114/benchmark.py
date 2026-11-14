#!/usr/bin/env python3
"""Out-of-folio word prediction on already filtered IVTFF; never reads repository data/ or HOLDOUT."""
import os,re,json,math,random,collections,hashlib,pathlib
seed=20261114
base=pathlib.Path(os.environ["VOYNICH_DATA_DIR"])
def parse(path):
 pages={};page=None
 for line in path.read_text(encoding="utf-8").splitlines():
  m=re.match(r"^<(f[0-9]+[rv][0-9]*)>\s+<!",line)
  if m:
   page=m.group(1);pages.setdefault(page,[]);continue
  if page is None or not re.match(r"^<f[0-9]+[rv][0-9]*\\.",line):continue
  if not re.match(r"^<f[0-9]+[rv][0-9]*\\.[^>]*[,@+]P[0-9]*>",line):continue
  if ">" not in line:continue
  body=line.split(">",1)[1].split("<!",1)[0]
  words=re.findall(r"[a-zA-Z]+",body.lower())
  if len(words)>1:pages[page].append(words)
 return pages
def evaluate(pages):
 ids=sorted(k for k,v in pages.items() if len(v)>=3)
 if len(ids)<15:return {"status":"INSUFFICIENT","folios":len(ids)}
 rng=random.Random(seed);rng.shuffle(ids)
 n=max(3,len(ids)//5);test=set(ids[:n]);train=set(ids[n:])
 uni=collections.Counter();bi=collections.Counter();vocab=set()
 for folio in train:
  for line in pages[folio]:
   for prev,w in zip(["<s>"]+line[:-1],line):
    uni[w]+=1;bi[(prev,w)]+=1;vocab.add(w)
 V=len(vocab)+1;total=sum(uni.values());prefix=collections.Counter()
 for (prev,w),v in bi.items():prefix[prev]+=v
 losses=[0.,0.];tokens=0
 for folio in test:
  for line in pages[folio]:
   for prev,w in zip(["<s>"]+line[:-1],line):
    p1=(uni[w]+.5)/(total+.5*V)
    p2=(bi[(prev,w)]+.5)/(prefix[prev]+.5*V)
    losses[0]-=math.log(p1);losses[1]-=math.log(p2);tokens+=1
 if not tokens:return {"status":"INSUFFICIENT_TEST_TOKENS"}
 return {"status":"EXPLORATORY_NOT_CI_VERIFIED","train_folios":len(train),"test_folios":len(test),"test_tokens":tokens,"unigram_nats_per_token":round(losses[0]/tokens,6),"bigram_nats_per_token":round(losses[1]/tokens,6),"bigram_gain_nats_per_token":round((losses[0]-losses[1])/tokens,6)}
out={"seed":seed,"method":"folio-heldout unigram vs add-half bigram, no tuning, IVTFF P lines","corpora":{}}
for name in ("ZL3b-n.txt","IT2a-n.txt"):
 p=base/name
 if not p.is_file():out["corpora"][name]={"status":"MISSING_SAFE_CORPUS"};continue
 out["corpora"][name]=evaluate(parse(p))
print(json.dumps(out,indent=2,sort_keys=True))
