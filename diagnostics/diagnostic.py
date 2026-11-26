"""Componenti proposti per la revisione. Nessun entry point di lancio."""
import csv
import hashlib
import io
import math
import os
import struct
from pathlib import Path

IDS = {(0, 4): range(212, 262), (0, 9): range(901, 911), (1, 1): range(901, 911)}
CORES = (None, 'Haswell', 'Zen', 'SkylakeX') * 2
THREADS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')
TARGETS = ('AVX512F AVX512CD AVX512_KNL AVX512_KNM AVX512_SKX AVX512_CLX '
           'AVX512_CNL AVX512_ICL AVX512_SPR AVX512_VBMI AVX512_VBMI2 '
           'AVX512_VNNI AVX512_BITALG AVX512_VPOPCNTDQ AVX512_FP16 AVX512_BF16 '
           'AVX512BW AVX512DQ AVX512VL AVX512IFMA AVX512ER AVX512PF '
           'AVX5124FMAPS AVX5124VNNIW').split()

def require(condition, reason):
    if not condition:
        raise ValueError(reason)

def environment(index, recognized, inherited):
    require(index in range(8), 'unknown configuration')
    env = dict(inherited)
    for name in ('OPENBLAS_CORETYPE', 'NPY_DISABLE_CPU_FEATURES'):
        env.pop(name, None)
    if CORES[index]:
        env['OPENBLAS_CORETYPE'] = CORES[index]
    if index >= 4:
        env['NPY_DISABLE_CPU_FEATURES'] = ','.join(t for t in TARGETS if t in recognized)
    env.update(dict.fromkeys(THREADS, '1'))
    return env

def verify_dispatch(index, pools, features, dispatch_targets, current_loops):
    # Call inside the child, after loading both wheels and before computing H1.
    for owner in ('numpy.libs', 'scipy.libs'):
        libs = [p for p in pools if p['user_api'] == 'blas'
                and owner in Path(p['filepath']).parts]
        require(len(libs) == 1, 'ambiguous BLAS owner: ' + owner)
        lib = libs[0]
        require(lib['internal_api'] == 'openblas' and lib['version'] == '0.3.30',
                'unsupported library')
        require(bool(lib.get('architecture')), 'unknown BLAS architecture')
        if CORES[index]:
            require(lib['architecture'].casefold() == CORES[index].casefold(),
                    'forced kernel not verified')
    require(all(p['num_threads'] == 1 for p in pools), 'thread limit')
    require(features and dispatch_targets and current_loops, 'missing SIMD evidence')
    if index >= 4:
        require(not any(features.get(t, False) for t in dispatch_targets
                        if t.startswith('AVX512')), 'AVX512 dispatch still available')
        require(all('AVX512' not in t.upper() for t in current_loops),
                'active AVX512 loop')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def compute_selected(driver, frozen, output, stream_reference):
    # Caller supplies a NEW private copy of verified driver+inputs per configuration.
    # No science on import. Requires approved preflight before invocation.
    require(not driver.WORK.exists(), 'work area already used')
    require(not os.sys.flags.optimize, 'frozen assertions are required')
    model = driver.setup(frozen)
    output.mkdir(exist_ok=False)
    result = {}
    for (g, r), ids in IDS.items():
        key = driver.label(g, r)
        shard = driver.OUT / key
        if shard.exists():
            # Preserve the extracted checkpoint, then let job() create a fresh shard.
            shard.rename(output / (key + '.checkpoint'))
        driver.adapt(model, ids=tuple(ids))((g, r))
        require((shard/'stream.sha256').read_text().strip() == stream_reference[key],
                'stream mismatch')
        raw = (shard/'reflow.csv').read_bytes().splitlines(keepends=True)
        require(len(raw) == len(ids) + 1 and all(s.endswith(b'\r\n') for s in raw),
                'row count or dialect')
        rows = list(csv.DictReader(io.StringIO(b''.join(raw).decode(), newline='')))
        fingerprints = {}
        for i, row, line in zip(ids, rows, raw[1:], strict=True):
            seed = f'20261124:502:{g}:{r}:{i}'
            require(row['seed'] == seed and row['reflow_id'] == str(i)
                    and row['geometry'] == driver.SERIES[g] and row['realization'] == str(r)
                    and row['status'] == 'OK' and row['error'] == ''
                    and row['n_transitions'] == str((2977,2936)[g]), 'unexpected row')
            value = float(row['gain_nats'])
            require(math.isfinite(value) and str(value) == row['gain_nats'], 'invalid gain')
            bits = struct.pack('>d', value)
            fingerprints[seed] = (sha(line), sha(bits), bits.hex())
        result[key] = (sha((shard/'H1.json').read_bytes()), fingerprints)
        shard.rename(output/key)
    return result

def review_candidate(reports, eligible):
    # eligible is the independently verified hardware-compatibility register,
    # keyed by the scheduled runner slot; unknown compatibility blocks a pass.
    slots = set(range(1,21))
    if set(eligible) != slots or set(reports) != slots:
        return False
    if any(type(eligible[s]) is not bool for s in slots):
        return False
    accepted = []
    for slot in sorted(slots):
        report = reports[slot]
        if eligible[slot]:
            if report['status'] != 'verified':
                return False
            accepted.append(report)
        elif report.get('status') != 'incompatible':
            return False
    models = {tuple(x['cpu_model']) for x in accepted}
    return (len(models) >= 2 and
            all(x['fingerprints'] == accepted[0]['fingerprints'] for x in accepted))
