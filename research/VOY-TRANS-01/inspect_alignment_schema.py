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
# Schema-only inspection; no tokens, values, predictions or gains emitted.
import inspect
def schema(x):
    if isinstance(x,dict): return {str(k):type(v).__name__ for k,v in x.items()}
    return type(x).__name__
out={}
for series in model.SERIES:
    p=hist.paragraphs[series][0]; r=hist.raw_rows[series][0]
    out[series]=dict(paragraph_schema=schema(p),row_schema=schema(r),n_rows=len(hist.raw_rows[series]))
out['read_paragraphs_source']=inspect.getsource(hist.old['read_paragraphs'])
out['score_source']=inspect.getsource(hist.old['score'])
(base.parent/'alignment_schema.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
