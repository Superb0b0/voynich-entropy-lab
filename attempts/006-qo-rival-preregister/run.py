#!/usr/bin/env python3
"""Preregistered exploratory qo test; reads only filtered training input."""
import collections, hashlib, json, os, random, re
from pathlib import Path
SEED=20261118
SHA='dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9'
N=1000

def parse(raw):
    groups=collections.defaultdict(list)
    page=''; leaf=0; para=0
    for line in raw.decode('utf-8').splitlines():
        m=re.match(r'^<(f\d+[rv]\d*)>',line)
        if m:
            page=m[1];leaf=int(re.match(r'f(\d+)',page)[1]);para=0;continue
        m=re.match(r'^<(f\d+[rv]\d*)\.(\d+),([^>]*)>\s*(.*)',line)
        if not m or m[1]!=page:continue
        n,loc,s=int(m[2]),m[3],m[4]
        if 'P' not in loc:continue
        if '*P' in loc or '@P' in loc:para+=1
        s=re.sub(r'<!.*?>|<[^>]*>|\{[^}]*\}|\[[^]]*\]','',s)
        tok=[re.sub('[^a-z]','',w.lower()) for w in re.split(r'[.,\s]+',s.strip())]
        tok=[w for w in tok if w]
        if tok:
            split=int(hashlib.sha256((str(leaf)+':20261114').encode()).hexdigest(),16)%2
            groups[(split,leaf,page,para)].append((n,tok[0]))
    return groups

def markov_model(words):
    transitions=collections.defaultdict(collections.Counter)
    for word in words:
        prev='^'
        for ch in word:
            transitions[prev][ch]+=1;prev=ch
    alphabet={p:(list(c),list(c.values())) for p,c in transitions.items()}
    return alphabet

def generate(rng,model,length):
    prev='^';out=[]
    for _ in range(length):
        chars,weights=model.get(prev,model['^'])
        ch=rng.choices(chars,weights,k=1)[0];out.append(ch);prev=ch
    return ''.join(out)

def count(groups,words_override=None):
    hit=den=0
    for i,rows in enumerate(groups):
        words=words_override[i] if words_override is not None else [x[1] for x in rows]
        for j in range(len(rows)-1):
            if rows[j+1][0]!=rows[j][0]+1:continue
            if words[j].startswith('qo'):
                den+=1;hit+=words[j+1].startswith('qo')
    return hit,den

def run(raw):
    parsed=parse(raw)
    out={'classification':'EXPLORATORY_TRAIN_ONLY','data_sha256':hashlib.sha256(raw).hexdigest(),
         'seed':SEED,'permutations':N,'scientific_validation':False,'splits':{}}
    tests=[]
    for split in (0,1):
        items=[(k,sorted(v)) for k,v in sorted(parsed.items()) if k[0]==split]
        groups=[v for _,v in items]
        words=[w for g in groups for _,w in g]
        model=markov_model(words)
        obs,den=count(groups)
        res={'folios':len({k[1] for k,_ in items}),'groups':len(groups),'observed':obs,'qo_predecessors':den,'rivals':{}}
        for ri,rival in enumerate(('paragraph_shuffle','char_markov')):
            rng=random.Random(SEED+split*10+ri)
            null=[]
            for iteration in range(N):
                fake=[]
                for g in groups:
                    ww=[w for _,w in g]
                    if rival=='paragraph_shuffle':rng.shuffle(ww)
                    else:ww=[generate(rng,model,len(w)) for w in ww]
                    fake.append(ww)
                hits,_=count(groups,fake)
                null.append(hits)
            null.sort()
            mean=sum(null)/N
            p=(1+sum(x<=obs for x in null))/(N+1)
            res['rivals'][rival]={'null_mean':mean,'null95':[null[25],null[974]],'p_one_sided':p,
                                  'obs_over_null':obs/mean if mean else None}
            tests.append((split,rival,p,obs/mean if mean else None))
        out['splits'][str(split)]=res
    indexed=sorted(enumerate(tests),key=lambda x:x[1][2]);adjusted=[0.0]*len(tests);prev=0
    for rank,(i,(_,_,p,_)) in enumerate(indexed):
        prev=max(prev,min(1.0,p*(len(tests)-rank)));adjusted[i]=prev
    out['holm_adjusted']={str(s)+'_'+r:adjusted[i] for i,(s,r,_,_) in enumerate(tests)}
    success=all(ratio is not None and ratio<.5 and adjusted[i]<=.01 for i,(_,_,_,ratio) in enumerate(tests))
    out['verdict']='EXPLORATORY_SIGNAL_ALL_RIVALS' if success else 'NOT_SUPPORTED_OR_INCONCLUSIVE'
    return out

def main():
    raw=(Path(os.environ['VOYNICH_DATA_DIR'])/'ZL3b-n.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise RuntimeError('Training SHA256 mismatch')
    result=run(raw)
    (Path(__file__).resolve().parent/'results_ci.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'splits':result['splits']},sort_keys=True))
if __name__=='__main__':main()
