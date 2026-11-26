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
# Score only the already admitted historical development rows. No raw corpus reload or HOLDOUT lookup.
results=[]
with threadpool_limits(limits=1):
    for g,series in enumerate(model.SERIES):
        rows=hist.raw_rows[series]
        assert len(rows)==(2977,2936)[g]
        assert model.geometry(rows)==model.geometry(hist.old['read_paragraphs'](hist.paragraphs[series]))
        y,p0,p1=hist.predict(rows)
        h=hist.old['score'](rows,y,p0,p1,np.ones(len(rows),dtype=bool))
        gain=float(h['gain']); ci=list(map(float,h['conditional_ci95']))
        results.append(dict(geometry=series,n_transitions=len(rows),gain=gain,conditional_ci95=ci,H1_valid=bool(ci[0]>0 and ci[0]>=.25*gain)))
(base.parent/'real_h1.json').write_text(json.dumps(dict(status='COMPLETE',scope='existing historical CAL-01 development rows only',results=results),indent=2)+'\n')
