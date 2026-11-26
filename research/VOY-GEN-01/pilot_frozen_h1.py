"""Exploratory A pilot with frozen historical H1 estimator; no reflow or holdout."""
import hashlib, json, os, sys, zipfile
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
base=Path(os.environ['CAL_STAGE']).resolve()
pkg=base/'cal01-actions-input.zip'
assert hashlib.sha256(pkg.read_bytes()).hexdigest()=='d962257994bb05d15e0f263d241f6d99fc28d63c4ea67b4f9dea5a6566d43da9'
private=base/'private'; private.mkdir()
with zipfile.ZipFile(pkg) as z:
    for name in ('driver.py','CAL01_CHECKPOINT_AUDIT.json','VOY-REFLOW-CAL-01_CHECKPOINT.zip'):
        (private/name).write_bytes(z.read(name))
assert hashlib.sha256((private/'VOY-REFLOW-CAL-01_CHECKPOINT.zip').read_bytes()).hexdigest()=='6043b1935029ba0e5b53e0cd9f65d0b70601b1d998e605840fa32cb805541a4d'
sys.path.insert(0,str(private))
import driver
model=driver.setup(base/'frozen')
assert hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()=='da78911c39f9f53a33f9404d7b59696a042ec60dbc6a9731d5fc60d9b4c186ac'
hist=model.hist
results=[]
with threadpool_limits(limits=1):
    for g,series in enumerate(model.SERIES):
        for seed in range(1,21):
            rng=np.random.default_rng(seed)
            ps=[]
            for p in hist.paragraphs[series]:
                prev=None; lines=[]
                for orig in p['lines']:
                    n=len(orig)
                    if n==0:
                        lines.append([]); continue
                    q=bool(rng.random()<(.25 if prev is None else .10 if prev else .30))
                    prev=q
                    # Interior tokens iid at stationary opening marginal; no real token copied.
                    lines.append(['qo' if q else 'd']+['qo' if u<.25 else 'd' for u in rng.random(n-1)])
                ps.append(dict(p,lines=lines))
            rows=model.rows_for(ps,g)
            assert len(rows)==(2977,2936)[g]
            y,p0,p1=hist.predict(rows)
            h=hist.old['score'](rows,y,p0,p1,np.ones(len(rows),dtype=bool))
            gain=float(h['gain']); ci=list(map(float,h['conditional_ci95']))
            results.append(dict(geometry=series,seed=seed,n_transitions=len(rows),gain=gain,conditional_ci95=ci,H1_valid=bool(ci[0]>0 and ci[0]>=.25*gain)))
out=dict(status='EXPLORATORY_COMPLETE',estimator='frozen historical CAL-01 predict and score via driver.setup',design='paragraph reset; opening P(q|q)=.10 P(q|other)=.30 initial=.25; iid interior .25; no reflow',results=results,counts={s:sum(r['H1_valid'] for r in results if r['geometry']==s) for s in model.SERIES})
Path('pilot_result.json').write_text(json.dumps(out,indent=2)+'\n')
