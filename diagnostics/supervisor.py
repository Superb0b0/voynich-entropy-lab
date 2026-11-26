"""Draft Actions runner. Install beside diagnostic.py in a reviewed checkout."""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import traceback
import zipfile
from pathlib import Path
import diagnostic as d

BASE = Path(os.environ.get('CAL_STAGE', '.')).resolve()
OUT = BASE/'evidence'
PINS = {'input.zip':'d962257994bb05d15e0f263d241f6d99fc28d63c4ea67b4f9dea5a6566d43da9',
        '15018135784.zip':'761292fa3157b379632f2097ed44cb524af507dd4760db305138a829f3862c33',
        '15017881677.zip':'91eb3dfc4d118cb2c4806d44f04c0ea5b5085636969558814fcece81206b150b',
        '15018760069.zip':'7f1758dcc88500484e4e5072419143e6d579ee9aeb49a91169f24107d4462002'}
ARTS = {(0,4):15018135784,(0,9):15017881677,(1,1):15018760069}

def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')

def original_references():
    from preflight import verify
    d.require(d.sha((BASE/'input.zip').read_bytes()) == PINS['input.zip'], 'frozen input')
    receipt = verify(BASE)
    save(OUT/'original-panel-provenance.json', receipt)
    streams = {}
    for (g,r), aid in ARTS.items():
        key = f'{("ZL3b","IT2a")[g]}_{r:02d}'
        with zipfile.ZipFile(BASE/f'{aid}.zip') as z:
            streams[key] = z.read('stream.sha256').decode().strip()
    return streams

def cpu():
    data = json.loads(subprocess.check_output(['lscpu','-J'],text=True))
    fields = {}
    def collect(entries):
        for entry in entries:
            fields[entry['field'].rstrip(':')] = entry.get('data')
            collect(entry.get('children', []))
    collect(data['lscpu'])
    return fields

def load_numpy():
    import numpy as np
    from numpy._core import _multiarray_umath as mu
    return np,mu

def worker(index):
    from importlib.metadata import version
    import scipy.linalg.blas
    import sklearn.linear_model
    from threadpoolctl import threadpool_info
    np,mu = load_numpy()
    stage = OUT/f'D{index:02d}'
    runtime = io.StringIO()
    with contextlib.redirect_stdout(runtime):
        np.show_runtime()
        np.show_config()
        import scipy
        scipy.show_config()
    versions = {name:version(name) for name in ('numpy','scipy','scikit-learn','threadpoolctl')}
    pools = threadpool_info()
    for pool in pools:
        pool["binary_sha256"] = d.sha(Path(pool["filepath"]).read_bytes())
    features = dict(mu.__cpu_features__)
    loops = np.lib.introspect.opt_func_info()
    env = {k:os.environ.get(k) for k in (*d.THREADS,'OPENBLAS_CORETYPE','NPY_DISABLE_CPU_FEATURES')}
    save(stage/'runtime.json', dict(cpu=cpu(),platform=platform.platform(),python=sys.version,
         packages=versions,features=features,dispatch=list(mu.__cpu_dispatch__),loops=loops,
         pools=pools,runtime=runtime.getvalue(),environment=env))
    d.require(platform.python_version()=='3.13.5' and
              [versions[k] for k in ('numpy','scipy','scikit-learn')]==['2.3.5','1.17.0','1.8.0'],
              'runtime versions')
    log64 = loops.get('log', {}).get('dd')
    d.require(log64 and log64.get('current'), 'float64 log dispatch unverifiable')
    current = [v['current'] for sig in loops.values() for v in sig.values()]
    d.verify_dispatch(index,pools,features,mu.__cpu_dispatch__,current)
    private = stage/'input'
    private.mkdir()
    with zipfile.ZipFile(BASE/'input.zip') as archive:
        for name in ('driver.py','VOY-REFLOW-CAL-01_CHECKPOINT.zip','CAL01_CHECKPOINT_AUDIT.json'):
            (private/name).write_bytes(archive.read(name))
    spec = importlib.util.spec_from_file_location('adapter',private/'driver.py')
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    streams = json.loads((OUT/'original-streams.json').read_text())
    result = d.compute_selected(adapter, BASE/'frozen', stage/'recomputed', streams)
    save(stage/'fingerprints.json',result)

def supervise():
    d.require(os.environ.get('GITHUB_RUN_ATTEMPT')=='1', 'attempt must be 1')
    OUT.mkdir(exist_ok=False)
    machine = cpu()
    save(OUT/'cpu.json',machine)
    shutil.copyfile('/etc/os-release',OUT/'os-release')
    save(OUT/'provenance.json',{'image':os.getenv('ImageOS'),'build':os.getenv('ImageVersion'),
        'packages':subprocess.check_output([sys.executable,'-m','pip','freeze','--all'],text=True),
        'inputs':PINS,'run':os.getenv('GITHUB_RUN_ID'),'slot':os.getenv('SLOT')})
    save(OUT/'original-streams.json',original_references())
    # A default management probe collects recognized targets; no estimator is imported.
    np,mu = load_numpy()
    recognized = list(mu.__cpu_dispatch__)
    cpu_key = [machine[k] for k in ('Vendor ID','CPU family','Model','Model name')]
    # Linux flags describe OS-enabled ISA. The unforced build independently
    # supplies the NumPy OS-state probe. Kernel identity is checked in each child.
    flags = set(machine['Flags'].split())
    d.require(platform.machine() == 'x86_64' and flags, 'missing x86 ISA evidence')
    baseline_features = dict(mu.__cpu_features__)
    save(OUT/'unforced-isa.json', dict(model=cpu_key, flags=sorted(flags),
             features=baseline_features, dispatch=recognized))
    failures = []
    for index,core in enumerate(d.CORES):
        stage = OUT/f'D{index:02d}'
        stage.mkdir()
        state = {'cpu_model':cpu_key,'stepping':machine.get('Stepping')}
        try:
            if core:
                required = {'avx','avx2','fma'}
                if core == 'SkylakeX':
                    required.update({'avx512f','avx512cd','avx512bw','avx512dq','avx512vl'})
                state['required_flags'] = sorted(required)
                missing = sorted(required - flags)
                if missing:
                    state.update(status='incompatible', missing_flags=missing)
                    continue
                required_numpy = ['AVX','AVX2','FMA3']
                if core == 'SkylakeX':
                    required_numpy.append('AVX512_SKX')
                d.require(all(baseline_features.get(f) for f in required_numpy),
                          'OS-enabled ISA not confirmed')
            env = d.environment(index,recognized,os.environ)
            with (stage/'process.log').open('wb') as log:
                subprocess.run([sys.executable,__file__,'worker',str(index)],env=env,stdout=log,
                               stderr=subprocess.STDOUT,check=True)
            state['status']='verified'
        except Exception:
            state.update(status='failed',detail=traceback.format_exc())
            failures.append(index)
        finally:
            save(stage/'status.json',state)
    return int(bool(failures))

if __name__ == '__main__':
    if len(sys.argv)==3 and sys.argv[1]=='worker':
        worker(int(sys.argv[2]))
    else:
        sys.exit(supervise())
