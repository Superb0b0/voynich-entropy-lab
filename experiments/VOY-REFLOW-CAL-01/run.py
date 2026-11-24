#!/usr/bin/env python3
"""CAL-01 adapter; no scientific execution without remote freeze receipt."""
import csv, hashlib, importlib.util, json, os, sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'reflow_execution'
N=1000; MASTER=20261124; SERIES=('ZL3b','IT2a')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rng(*key): return np.random.Generator(np.random.PCG64(np.random.SeedSequence([MASTER,*key])))
def stream(T, random):
    a=13; out=[]
    for u in random.random(T+256):
        q=u < (.01 if a<=12 else .20)
        out.append('qo' if q else 'd'); a=1 if q else min(a+1,13)
    return out[256:]
def split(tokens,lens):
    out=[]; offset=0
    for n in lens: out.append(tokens[offset:offset+n]); offset+=n
    assert offset==len(tokens); return out
def init():
    global hist
    spec=importlib.util.spec_from_file_location('historical',SRC/'execute.py'); hist=importlib.util.module_from_spec(spec); spec.loader.exec_module(hist); hist.initialize()
def synth(g,r):
    random=rng(501,g,r); out=[]
    for p in hist.paragraphs[SERIES[g]]:
        lens=list(map(len,p['lines'])); tokens=stream(sum(lens),random)
        out.append(dict(p,lines=split(tokens,lens)))
    return out
def geometry(rows): return [(r['folio'],r['leaf'],r['fold'],r['pos'],r['length'],r['section'],r['source_row']) for r in rows]
def rows_for(ps,g):
    rows=hist.old['read_paragraphs'](ps)
    assert geometry(rows)==geometry(hist.raw_rows[SERIES[g]])
    return rows
def classify(h1,a):
    g=h1['gain']; l=h1['conditional_ci95'][0]; valid=l>0 and l>=.25*g
    m=float(a.mean()); k=int((a>=g).sum()); p=(k+1)/1001; rho=m/g if g else None; lo,hi=np.quantile(a,[.025,.975],method='linear').tolist()
    cat='I'
    if valid and hi>=0 and rho is not None:
        if p<=.05 and rho<=.25: cat='R'
        elif p>.05 and rho>=.75: cat='C'
    return dict(H1_valid=bool(valid),G0=g,L0=l,mean=m,sd=float(a.std(ddof=1)),rho=rho,k=k,p=p,percentiles=[lo,hi],category=cat)
def job(task):
    g,r=task; ps=synth(g,r); rows=rows_for(ps,g); y,p0,p1=hist.predict(rows); h1=hist.old['score'](rows,y,p0,p1,np.ones(len(rows),dtype=bool)); out=ROOT/'output'/f'{SERIES[g]}_{r:02d}'; out.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(ps,separators=(',',':')).encode(); (out/'stream.sha256').write_text(hashlib.sha256(payload).hexdigest()+'\n'); (out/'H1.json').write_text(json.dumps(h1,indent=2)+'\n')
    path=out/'reflow.csv'; fields=['geometry','realization','reflow_id','seed','n_transitions','gain_nats','status','error']; prev=[]
    if path.exists():
        with path.open() as f: prev=list(csv.DictReader(f))
        assert all(int(v['reflow_id'])==i and v['seed']==f'{MASTER}:502:{g}:{r}:{i}' and v['status']=='OK' for i,v in enumerate(prev,1))
    a=[float(v['gain_nats']) for v in prev]; inp=[dict(folio=p['folio'],lang=p['section'],words=p['lines']) for p in ps]
    with path.open('a',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        if not prev:w.writeheader()
        for i in range(len(prev)+1,N+1):
            seed=f'{MASTER}:502:{g}:{r}:{i}'
            try:
                new=hist.rf['reflow_one'](inp,rng(502,g,r,i)); assert len(new)==len(ps); transformed=[]
                for orig,v in zip(ps,new):
                    assert orig['folio']==v['folio'] and orig['section']==v['lang']; assert sum(orig['lines'],[])==sum(v['words'],[]); assert sorted(map(len,orig['lines']))==sorted(map(len,v['words'])); transformed.append(dict(orig,lines=v['words']))
                rr=rows_for(transformed,g); gain=hist.gain(*hist.predict(rr)); assert np.isfinite(gain); a.append(gain)
                w.writerow(dict(geometry=SERIES[g],realization=r,reflow_id=i,seed=seed,n_transitions=len(rr),gain_nats=gain,status='OK',error='')); f.flush()
            except Exception as e:
                w.writerow(dict(geometry=SERIES[g],realization=r,reflow_id=i,seed=seed,status='ERROR',error=repr(e))); f.flush(); raise
    tokens=sum((sum(p['lines'],[]) for p in ps),[]); openings=[line[0] for p in ps for line in p['lines'] if line]; result=classify(h1,np.asarray(a)); result.update(geometry=SERIES[g],realization=r,qo_frequency=tokens.count('qo')/len(tokens),qo_opening_frequency=openings.count('qo')/len(openings)); (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n'); return result
def gate():
    m=json.loads((ROOT/'FREEZE_MANIFEST.json').read_text()); receipt=json.loads((ROOT/'REMOTE_RECEIPT.json').read_text()); assert receipt['remote_verified'] is True and receipt['manifest_sha256']==sha(ROOT/'FREEZE_MANIFEST.json') and receipt['commit'] and receipt['observed_at_utc']
    for n,d in m['local_files'].items(): assert sha(ROOT/n)==d,n
    for n,d in m['historical_files'].items(): assert sha(SRC/n)==d,n
    import sklearn, scipy, platform
    assert m['environment']==dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,sklearn=sklearn.__version__)
def main():
    gate(); init()
    # Technical invariance: same stream with distinct line segmentations.
    a=stream(24,rng(501,99,1)); b=stream(24,rng(501,99,1)); assert sum(split(a,[9,8,7]),[])==sum(split(b,[7,9,8]),[])
    with ProcessPoolExecutor(max_workers=4,initializer=init) as pool:
        results=list(pool.map(job,[(g,r) for g in range(2) for r in range(1,21)]))
    counts={s:{c:sum(v['geometry']==s and v['category']==c for v in results) for c in 'CRI'} for s in SERIES}; h={s:sum(v['geometry']==s and v['H1_valid'] for v in results) for s in SERIES}
    verdict='CONTROESEMPIO' if any(v['R'] for v in counts.values()) else 'NON QUALIFICATO' if min(h.values())<16 else 'CONSERVAZIONE FREQUENTE' if all(v['C']>=16 for v in counts.values()) else 'INCONCLUDENTE'
    (ROOT/'output'/'aggregate.json').write_text(json.dumps(dict(counts=counts,H1_valid=h,verdict=verdict,results=results),indent=2)+'\n')
if __name__=='__main__': main()
