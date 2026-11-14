#!/usr/bin/env python3
"""Preregistered exploratory qo test; reads only filtered training input."""
import collections, hashlib, json, os, random, re
from pathlib import Path
SEED=20261119
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
    out={'classification':'EXPLORATORY_CONDITIONAL_RATE','data_sha256':hashlib.sha256(raw).hexdigest(),
         'seed':SEED,'simulations':N,'scientific_validation':False,'splits':{}}
    tests=[]
    for split in (0,1):
        items=[(k,sorted(v)) for k,v in sorted(parsed.items()) if k[0]==split]
        groups=[v for _,v in items]
        words=[w for g in groups for _,w in g]
        model=markov_model(words)
        obs,den=count(groups)
        if not den:raise RuntimeError('zero observed denominator')
        observed_rate=obs/den
        successors=[]
        for g in groups:
            for i in range(len(g)-1):
                if g[i+1][0]==g[i][0]+1 and g[i][1].startswith('qo'):
                    successors.append(g[i+1][1])
        assert len(successors)==den
        res={'folios':len({k[1] for k,_ in items}),'groups':len(groups),'observed_hits':obs,
             'observed_denominator':den,'observed_rate':observed_rate,'rivals':{}}
        for ri,rival in enumerate(('paragraph_shuffle_rate','fixed_predecessor_char_markov')):
            rng=random.Random(SEED+split*10+ri)
            null=[];zeros=0
            for iteration in range(N):
                if ri==0:
                    fake=[]
                    for g in groups:
                        ww=[w for _,w in g];rng.shuffle(ww);fake.append(ww)
                    nh,nd=count(groups,fake)
                    if nd==0:zeros+=1;continue
                    null.append(nh/nd)
                else:
                    nh=sum(generate(rng,model,len(w)).startswith('qo') for w in successors)
                    null.append(nh/den)
            if not null:raise RuntimeError('all zero denominator')
            null.sort();mean=sum(null)/len(null)
            p=(1+sum(v<=observed_rate for v in null))/(len(null)+1)
            quantiles=[null[int(.025*(len(null)-1))],null[int(.975*(len(null)-1))]]
            res['rivals'][rival]={'null_mean_rate':mean,'null95_rate':quantiles,
                'p_one_sided':p,'obs_over_null_rate':observed_rate/mean if mean else None,
                'zero_denominator_draws':zeros}
            tests.append((split,rival,p,observed_rate/mean if mean else None,zeros))
        out['splits'][str(split)]=res
    indexed=sorted(enumerate(tests),key=lambda x:x[1][2]);adjusted=[0.0]*len(tests);prev=0
    for rank,(i,(_,_,p,_,_)) in enumerate(indexed):
        prev=max(prev,min(1.0,p*(len(tests)-rank)));adjusted[i]=prev
    out['holm_adjusted']={str(sp)+'_'+r:adjusted[i] for i,(sp,r,_,_,_) in enumerate(tests)}
    success=all(ratio is not None and ratio<.5 and adjusted[i]<=.01 and zeros==0
                for i,(_,_,_,ratio,zeros) in enumerate(tests))
    out['verdict']='EXPLORATORY_THRESHOLD_MET' if success else 'NOT_SUPPORTED_OR_INCONCLUSIVE'
    return out

def main():
    raw=(Path(os.environ['VOYNICH_DATA_DIR'])/'ZL3b-n.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise RuntimeError('Training SHA256 mismatch')
    result=run(raw)
    (Path(__file__).resolve().parent/'results_ci.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
