"""Fresh D05 shard. The parent checks the CPU before starting the numeric process."""
import csv
import hashlib
import io
import json
import math
import os
import platform
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'diagnostics'))
import diagnostic as d
from supervisor import cpu
REF = json.loads((HERE/'reference.json').read_text())
BASE = Path(os.environ['CAL_STAGE']).resolve()
OUT = BASE/'result'
EPS = 1000 * 9.163456018285165e-12
FIELDS = 'geometry realization reflow_id seed n_transitions gain_nats status error'.split()

def validate(raw, previous, g, r):
    series = ('ZL3b','IT2a')[g]
    records = csv.DictReader(io.StringIO(raw.decode('ascii'),newline=''))
    old = list(csv.DictReader(io.StringIO(previous.decode('ascii'),newline='')))
    lines = raw.splitlines(True)
    d.require(records.fieldnames==FIELDS and len(lines)==1001,'CSV shape')
    peak = 0.0
    for i,(row,line) in enumerate(zip(records,lines[1:],strict=True),1):
        seed = f'20261124:502:{g}:{r}:{i}'
        d.require(None not in row and None not in row.values() and line.endswith(b'\r\n'),'CSV dialect')
        d.require([row[k] for k in FIELDS[:5]]==[series,str(r),str(i),seed,str((2977,2936)[g])] and
                  row['status']=='OK' and row['error']=='','row identity')
        gain = float(row['gain_nats'])
        d.require(math.isfinite(gain) and str(gain)==row['gain_nats'],'gain')
        if seed in REF['rows']:
            d.require([d.sha(line),d.sha(struct.pack('>d',gain))]==REF['rows'][seed],'canonical D05 anchor')
        if i<=len(old):
            prior=old[i-1]
            d.require(all(prior[k]==row[k] for k in FIELDS if k!='gain_nats'),'checkpoint identity')
            old_gain=float(prior['gain_nats'])
            d.require(math.isfinite(old_gain),'historical gain')
            peak=max(peak,abs(old_gain-gain))
    return len(old),peak

def child(g,r):
    import numpy as np
    from numpy._core import _multiarray_umath as mu
    import scipy.linalg.blas
    import sklearn.linear_model
    from threadpoolctl import threadpool_info
    pools=threadpool_info()
    loops=np.lib.introspect.opt_func_info()
    bits={Path(p['filepath']).name:d.sha(Path(p['filepath']).read_bytes()) for p in pools}
    env={k:os.environ.get(k) for k in REF['env']}
    runtime=dict(cpu=cpu(),env=env,features=mu.__cpu_features__,targets=mu.__cpu_dispatch__,
                 log64=loops['log']['dd']['current'],pools=pools,binaries=bits,
                 image=os.getenv('ImageOS'),build=os.getenv('ImageVersion'),run=os.getenv('GITHUB_RUN_ID'))
    (OUT/'runtime.json').write_text(json.dumps(runtime,indent=2))
    d.require(platform.python_version()=='3.13.5' and env==REF['env'] and bits==REF['libs'],'pinned build')
    d.verify_dispatch(5,pools,mu.__cpu_features__,mu.__cpu_dispatch__,[v['current'] for s in loops.values() for v in s.values()])
    d.require(runtime['log64']=='AVX2','log float64')
    src=BASE/'cal01-actions-input.zip'
    d.require(d.sha(src.read_bytes())=='d962257994bb05d15e0f263d241f6d99fc28d63c4ea67b4f9dea5a6566d43da9','input')
    private=BASE/'private'
    private.mkdir()
    with zipfile.ZipFile(src) as z:
        for name in ('driver.py','CAL01_CHECKPOINT_AUDIT.json','VOY-REFLOW-CAL-01_CHECKPOINT.zip'):
            (private/name).write_bytes(z.read(name))
    sys.path.insert(0,str(private))
    import driver
    model=driver.setup(BASE/'frozen')
    key=driver.label(g,r)
    shard=driver.OUT/key
    previous=driver.prefix(key)
    if shard.exists():
        shard.rename(BASE/'historical-copy')
    d.require(not shard.exists() and not sys.flags.optimize,'fresh shard')
    model.job((g,r))
    count,peak=validate((shard/'reflow.csv').read_bytes(),previous,g,r)
    expected=driver.SAMPLES.get(key,{})
    d.require(count==expected.get('rows',0),'control count')
    if expected:
        d.require((shard/'stream.sha256').read_text().strip()==expected['stream_sha256'],'stream')
    if key in REF['h1']:
        d.require(driver.sha(shard/'H1.json')==REF['h1'][key],'canonical D05 H1')
    for name in ('reflow.csv','H1.json','stream.sha256','summary.json'):
        (shard/name).rename(OUT/name)
    manifest=dict(key=key,g=g,r=r,rows=1000,controls=count,max_delta=peak,epsilon=EPS,
                  within=peak<=EPS,files={p.name:driver.sha(p) for p in OUT.iterdir()})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    d.require(peak<=EPS,'historical gain outside envelope')

if __name__=='__main__':
    g,r=map(int,sys.argv[1:3])
    d.require(g in (0,1) and 1<=r<=20,'shard')
    if sys.argv[3:]==['worker']:
        child(g,r)
    else:
        OUT.mkdir(exist_ok=False)
        host=cpu()
        model=[host[k] for k in ('Vendor ID','CPU family','Model','Model name')]
        d.require(model in REF['models'] and {'avx','avx2','fma'}<=set(host['Flags'].split()),'supported CPU')
        env=dict(os.environ,**REF['env'])
        env.pop('NPY_ENABLE_CPU_FEATURES',None)
        subprocess.run([sys.executable,__file__,str(g),str(r),'worker'],env=env,check=True)
