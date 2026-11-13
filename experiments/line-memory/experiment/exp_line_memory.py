#!/usr/bin/env python3
"""EXP-SEQ-LINE-MEMORY-01: read-only P-only line-order randomization.
Predeclared statistics: (1) set Jaccard, (2) mean within-row exact-token reuse,
(3) mean within-row edit-distance-one exposure excluding identity.
Nulls: folio order, paragraph order, paragraph order with endpoints fixed.
No builder, clustering, image-text coupling, or alterations to sources.
"""
import re, json, hashlib, importlib.util, csv
from pathlib import Path
from collections import defaultdict, Counter
from functools import lru_cache
import numpy as np

BASE=(Path(__file__).resolve().parent/'inputs' if (Path(__file__).resolve().parent/'inputs').exists() else Path('/mnt/data/voynich_experiments'))
OUT=Path(__file__).resolve().parent
N_PERM=1999
SEED=20261112
TOK=BASE/'zl3b_P_ms408.tsv'
SRC=BASE/'ZL3b-n.txt'
PARSER=BASE/'ivtff_parser_rc1_2.py'
HASHES={'ZL3b-n.txt':'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc',
        'zl3b_P_ms408.tsv':'41c3ea40b7f71ea612fbee49a65ebd253231a209ce2d5096131126c957bcd1f2'}
for file,expect in HASHES.items():
    got=hashlib.sha256((BASE/file).read_bytes()).hexdigest()
    assert got==expect, (file,got)

def load():
    spec=importlib.util.spec_from_file_location('immutable_parser',PARSER)
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    full=parser.parse_corpus(SRC)
    rec=full['records']
    raw=SRC.read_text().splitlines()
    rows=[]
    for ln in TOK.read_text().splitlines():
        folio,body=ln.split('\t');rows.append((folio,body.split()))
    assert len(rec)==len(rows)==4130
    assert all(z['folio']==x[0] for z,x in zip(rec,rows))
    head={}
    for ln in raw:
        m=re.match(r'^<([^>,.]+)>\s*<!',ln)
        if m:
            lang=re.search(r'\$L=([^\s>]+)',ln)
            hand=re.search(r'\$H=([^\s>]+)',ln)
            head[m[1]]={'currier':lang[1] if lang else '?','hand':hand[1] if hand else '?'}
    folios=defaultdict(list);paras=defaultdict(list)
    for i, (z,(f, words)) in enumerate(zip(rec,rows)):
        folios[f].append(i)
        line=raw[z['physical_line']-1]
        if '<%>' in line or not paras[f]: paras[f].append([])
        paras[f][-1].append(i)
    return rows,head,folios,paras

@lru_cache(maxsize=750000)
def edit1(a,b):
    if a==b:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if len(a)+1==len(b):return any(b[:i]+b[i+1:]==a for i in range(len(b)))
    if len(b)+1==len(a):return any(a[:i]+a[i+1:]==b for i in range(len(a)))
    return False

rows,meta,folios,paras=load()
words=[tuple(ws) for _,ws in rows]
sets=[set(ws) for ws in words]

def pair_metrics(i,j):
    """Directed i→j; exact rate/e1 denominator is token count in row j."""
    a,b=sets[i],sets[j]
    both=len(a&b)
    jac=both/(len(a)+len(b)-both) if a or b else 0.0
    d=len(words[j]);exact=sum(w in a for w in words[j])/d
    # A different word one Levenshtein edit away, not the identical token.
    ed=sum(any(edit1(w,p) for p in a) for w in words[j])/d
    return jac,exact,ed

# Pairwise panels within each folio, 0-based local positions.
folio_data=[]
for f,ids in folios.items():
    ids=list(ids);index={g:i for i,g in enumerate(ids)};n=len(ids)
    M=np.zeros((3,n,n),dtype=np.float64)
    for x in range(n):
        for y in range(n):
            if x!=y:
                M[:,x,y]=pair_metrics(ids[x],ids[y])
    P=[np.array([index[k] for k in group],dtype=np.int32) for group in paras[f]]
    folio_data.append({'folio':f,'currier':meta[f]['currier'],'hand':meta[f]['hand'],
                       'matrix':M,'original':np.arange(n,dtype=np.int32),'paragraphs':P,
                       'n':n,'edges_folio':n-1,'edges_para':sum(len(x)-1 for x in P)})

# Observed separate within-paragraph & across-paragraph, each same-folio.
def panel_edges(M,pairs):
    if not pairs:return np.zeros(3)
    aa=np.array([i for i,j in pairs],dtype=np.int32)
    bb=np.array([j for i,j in pairs],dtype=np.int32)
    return M[:,aa,bb].sum(axis=1)

def obs_panel(x,mode):
    M=x['matrix']
    if mode=='folio':
        ind=x['original'];return M[:,ind[:-1],ind[1:]].sum(axis=1)
    if mode=='para':
        return sum((M[:,p[:-1],p[1:]].sum(axis=1) for p in x['paragraphs'] if len(p)>1),np.zeros(3))
    if mode=='boundary':
        z=x['paragraphs'];return panel_edges(M,[(z[i][-1],z[i+1][0]) for i in range(len(z)-1)])
    if mode=='para_endpoints':
        return sum((M[:,p[:-1],p[1:]].sum(axis=1) for p in x['paragraphs'] if len(p)>=4),np.zeros(3))
    raise ValueError(mode)

rng=np.random.default_rng(SEED)
N=len(folio_data)
obs={mode:np.array([obs_panel(x,mode) for x in folio_data])
    for mode in ['folio','para','boundary','para_endpoints']}
counts={mode:np.array([x['edges_folio'] if mode=='folio' else x['edges_para'] if mode=='para' else len(x['paragraphs'])-1 if mode=='boundary'
                      else sum(len(p)-1 for p in x['paragraphs'] if len(p)>=4) for x in folio_data],dtype=np.int32)
        for mode in obs}
obs_mean={mode:obs[mode].sum(axis=0)/sum(counts[mode]) for mode in obs}

null={mode:np.zeros((N_PERM,3),dtype=float) for mode in ['folio','para','para_endpoints']}
# for cluster bootstrap: mean null per folio row, three stats.
null_sum_by_folio={mode:np.zeros((N,3),dtype=float) for mode in null}
# by Currier, collect empirical obs and null distributions.
currier={s:np.array([i for i,x in enumerate(folio_data) if x['currier']==s],dtype=int) for s in ['A','B','?']}
currier_null={mode:{s:np.zeros((N_PERM,3)) for s in ['A','B','?']} for mode in null}

for k in range(N_PERM):
    for j,x in enumerate(folio_data):
        M=x['matrix']
        # Null F: random permutation of all rows inside each folio.
        q=rng.permutation(x['original'])
        v=M[:,q[:-1],q[1:]].sum(axis=1)
        null['folio'][k]+=v
        null_sum_by_folio['folio'][j]+=v
        # Null P: random permutation of rows within each paragraph, keeping paragraphs & folio.
        v=np.zeros(3)
        w=np.zeros(3)
        for p in x['paragraphs']:
            if len(p)<2:continue
            q=rng.permutation(p)
            v+=M[:,q[:-1],q[1:]].sum(axis=1)
            if len(p)>=4:
                # Null EP: first & last paragraph lines fixed, only interior shuffled.
                z=p.copy();z[1:-1]=rng.permutation(z[1:-1])
                w+=M[:,z[:-1],z[1:]].sum(axis=1)
        null['para'][k]+=v
        null['para_endpoints'][k]+=w
        null_sum_by_folio['para'][j]+=v
        null_sum_by_folio['para_endpoints'][j]+=w
    # Currier nulls calculated later via independent trial rerun? Store per-folio K too expensive;
    # for now only cluster uncertainty globally.

results={}
for mode in null:
    n_edges=int(sum(counts[mode]));total=null[mode]/n_edges;observed=obs_mean[mode]
    results[mode]={'edges':n_edges,'observed':{},'null':{},'test':{}}
    for j,s in enumerate(['jaccard','exact_reuse','edit1_nonidentical']):
        values=total[:,j];o=observed[j]
        results[mode]['observed'][s]=float(o)
        results[mode]['null'][s]={'mean':float(values.mean()),'sd':float(values.std(ddof=1)),
                 'q025':float(np.quantile(values,.025)),'q975':float(np.quantile(values,.975))}
        results[mode]['test'][s]={'diff':float(o-values.mean()),'ratio':float(o/values.mean()) if values.mean()>0 else None,
                 'p_one_sided_above':float((1+np.count_nonzero(values>=o))/(N_PERM+1)),
                 'p_one_sided_below':float((1+np.count_nonzero(values<=o))/(N_PERM+1))}

# Group bootstrap, resampling folios preserving their paragraph structure; obs-versus-mean(null) diff per folio.
BR=2499
boot=np.random.default_rng(SEED+2)
for mode in null:
    n=counts[mode]
    expected=null_sum_by_folio[mode]/N_PERM
    delta=obs[mode]-expected
    values=np.zeros((BR,3))
    for b in range(BR):
        ix=boot.integers(0,N,N)
        values[b]=delta[ix].sum(axis=0)/n[ix].sum()
    for j,s in enumerate(['jaccard','exact_reuse','edit1_nonidentical']):
        results[mode]['test'][s]['bootstrap_diff_q025']=float(np.quantile(values[:,j],.025))
        results[mode]['test'][s]['bootstrap_diff_q975']=float(np.quantile(values[:,j],.975))

# Observational descriptives.
results['observed_boundaries']={mode:{'edges':int(counts[mode].sum()),**dict(zip(['jaccard','exact_reuse','edit1_nonidentical'],obs_mean[mode].tolist()))}
                                for mode in ['para','boundary','folio']}
results['currier_observational']={}
for group,ix in currier.items():
    if len(ix)==0:continue
    row={'folio_count':len(ix)}
    for mode in ['para','boundary','folio']:
        denom=counts[mode][ix].sum()
        row[mode]={ 'edges':int(denom),**({s:float(v) for s,v in zip(['jaccard','exact_reuse','edit1_nonidentical'],obs[mode][ix].sum(axis=0)/denom)} if denom else {})}
    results['currier_observational'][group]=row

payload={'experiment':'EXP_SEQ_LINE_MEMORY_01','date':'2026-11-12','status':'ESPLORATIVO','input_sha256':HASHES,
         'parser_sha256':hashlib.sha256(PARSER.read_bytes()).hexdigest(),
         'config':{'seed':SEED,'permutations':N_PERM,'bootstrap_resamples_folio':BR,'measures':['jaccard','exact_reuse','edit1_nonidentical'],
                   'nulls':['folio','para','para_endpoints'],'equal_weight_per_adjacent_edge':True},
         'sample':{'folios':N,'P_rows':len(rows),'P_tokens':sum(len(w) for w in words),'paragraphs':sum(len(x['paragraphs']) for x in folio_data),
                   'rows_in_para>=4':sum(sum(len(p) for p in x['paragraphs'] if len(p)>=4) for x in folio_data),
                   'currier_folio_counts':{k:int(len(v)) for k,v in currier.items()}},
         'results':results,
         'warnings':['P-only rows include original ZL3b punctuation/glyph conventions. Editing distance is literal on normalized P TSV words.',
                     'Permutation tests reject local exchangeability only, not prove self-citation or meaning.',
                     'First and last fixed null contains fewer effective randomizations; para<=3 excluded for this null.',
                     'This is exploratory new analysis of an already studied corpus; must not be represented as unexposed validation.']}
(OUT/'results.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False))
with (OUT/'permutation_distributions.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['iteration','null','jaccard','exact_reuse','edit1_nonidentical'])
    for mode,matrix in null.items():
        for k,v in enumerate(matrix/counts[mode].sum()):w.writerow([k+1,mode,*[f'{x:.8f}' for x in v]])
print('sample',payload['sample'])
for mode in ['folio','para','para_endpoints']:
    print('\n',mode,'edges=',results[mode]['edges'])
    for m in ['jaccard','exact_reuse','edit1_nonidentical']:
        print(m,'observed',round(results[mode]['observed'][m],6),'null',round(results[mode]['null'][m]['mean'],6),'p_above',results[mode]['test'][m]['p_one_sided_above'],'ratio',round(results[mode]['test'][m]['ratio'],3),'boot-diff',round(results[mode]['test'][m]['bootstrap_diff_q025'],5),round(results[mode]['test'][m]['bootstrap_diff_q975'],5))
print('boundary',results['observed_boundaries'])
