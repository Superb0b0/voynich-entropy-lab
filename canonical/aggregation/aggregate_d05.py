#!/usr/bin/env python3
"""CAL-01 D05 aggregation candidate. Source review required before reading artifacts."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import platform
import re
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERIES = ('ZL3b', 'IT2a')
KEYS = [(g, r) for g in range(2) for r in range(1, 21)]
FIELDS = 'geometry realization reflow_id seed n_transitions gain_nats status error'.split()
# Geometry invariant from original driver.rows and canonical matrix.validate (frozen input).
TRANSITIONS = (2977, 2936)
MEMBERS = {'runtime.json', 'reflow.csv', 'H1.json', 'stream.sha256', 'summary.json'}
FROZEN = '0fb8b0ddb2ab1281758834e501f166669646518e'
RUN_SHA = 'da78911c39f9f53a33f9404d7b59696a042ec60dbc6a9731d5fc60d9b4c186ac'
MANIFEST_BLOB = 'd98fd98a8933752ab64b33a01e96ac94411ae8ce'
INDEX_BLOB = '162774b8dc577bac950fc3e14a920b75dc0744cf'
REF_BLOB = '76508a08143fa2fcfc6d96d892920c56cf8cc806'
PACKAGE_SHA = 'd962257994bb05d15e0f263d241f6d99fc28d63c4ea67b4f9dea5a6566d43da9'
CHECKPOINT_SHA = '6043b1935029ba0e5b53e0cd9f65d0b70601b1d998e605840fa32cb805541a4d'
EPS = 1000 * 9.163456018285165e-12
# Proposed conservative audit allocation, for independent approval before execution.
# Not new scientific thresholds; the empirical envelope is not a universal bound.
E_GAIN = E_G0 = E_L0 = EPS

class Incomplete(Exception):
    pass

class Locked(Exception):
    pass


def need(ok, reason):
    if not ok:
        raise Incomplete(reason)


def lock(ok, reason):
    if not ok:
        raise Locked(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def pairs(items):
    out = {}
    for k, v in items:
        need(k not in out, 'duplicate JSON key')
        out[k] = v
    return out


def reject_constant(_):
    raise Incomplete('nonfinite JSON constant')


def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)


def read(path):
    return parse(Path(path).read_bytes())


def finite(x):
    return type(x) in (int, float) and math.isfinite(x)


def label(g, r):
    return f'{SERIES[g]}_{r:02d}'


def source_run(g, r):
    if (g, r) == (1, 6):
        return 45821985054
    if (g, r) in {(0, 7), (0, 19), (1, 5)}:
        return 45818815963
    return 45817324636


def sources(args):
    code = sha(Path(__file__).read_bytes())
    index_raw = args.index.read_bytes()
    ref_raw = args.reference.read_bytes()
    manifest_raw = (args.frozen / 'FREEZE_MANIFEST.json').read_bytes()
    lock(blob(index_raw) == INDEX_BLOB and blob(ref_raw) == REF_BLOB, 'source index/reference pin')
    lock(blob(manifest_raw) == MANIFEST_BLOB, 'freeze manifest pin')
    manifest = parse(manifest_raw)
    lock(manifest['local_files']['run.py'] == RUN_SHA, 'manifest run.py pin')
    for name, digest in manifest['local_files'].items():
        lock(sha((args.frozen / name).read_bytes()) == digest, 'frozen source bytes')
    lock(args.split_receipt.is_file(), 'split receipt missing')
    split_raw = args.split_receipt.read_bytes()
    split = parse(split_raw)
    lock(split['result'] == 'PASS' and split['source_sha256'] == RUN_SHA, 'split receipt')
    pins = dict(code_sha256=code, index_sha256=sha(index_raw), reference_sha256=sha(ref_raw),
                split_receipt_sha256=sha(split_raw), frozen_commit=FROZEN, run_sha256=RUN_SHA,
                manifest_sha256=sha(manifest_raw))
    # An attestation is a procedural gate, not cryptographic proof of independence.
    lock(args.review.is_file(), 'independent source review missing')
    review_raw = args.review.read_bytes()
    review = parse(review_raw)
    lock(review.get('approved') is True and review.get('independent_review') is True and
         isinstance(review.get('reviewer'), str) and bool(review['reviewer'].strip()) and
         re.fullmatch('[0-9a-f]{40}', review.get('reviewed_commit', '')) and
         review.get('pins') == pins and review.get('audit_allocation_approved') is True,
         'independent source review not approved for exact bytes')
    pins['review_sha256'] = sha(review_raw)
    return parse(index_raw), parse(ref_raw), manifest, pins


def zip_members(z):
    names = z.namelist()
    need(len(names) == len(set(names)), 'duplicate ZIP member')
    return set(names)


def cpu_ok(cpu, ref):
    model = [cpu[k] for k in ('Vendor ID', 'CPU family', 'Model', 'Model name')]
    return model in ref['models'] and {'avx', 'avx2', 'fma'} <= set(cpu['Flags'].split())


def runtime_ok(rt, ref):
    need(cpu_ok(rt['cpu'], ref), 'CPU not admitted')
    need(rt['env'] == ref['env'] and rt['binaries'] == ref['libs'], 'D05 build/environment')
    need(rt['log64'] == 'AVX2' and bool(rt['image']) and bool(rt['build']), 'D05 SIMD/image provenance')
    need(bool(rt['features']) and bool(rt['targets']) and
         not any(rt['features'].get(t, False) for t in rt['targets'] if t.startswith('AVX512')),
         'AVX512 dispatch')
    for owner in ('numpy.libs', 'scipy.libs'):
        libs = [p for p in rt['pools'] if p['user_api'] == 'blas' and owner in Path(p['filepath']).parts]
        need(len(libs) == 1 and libs[0]['internal_api'] == 'openblas' and
             libs[0]['version'] == '0.3.30' and libs[0]['architecture'].casefold() == 'haswell',
             'BLAS owner/kernel')
    need(all(p['num_threads'] == 1 for p in rt['pools']), 'thread limit')


def read_rows(raw, g, r, n):
    lines = raw.splitlines(keepends=True)
    rd = csv.DictReader(io.StringIO(raw.decode('ascii'), newline=''))
    need(rd.fieldnames == FIELDS and len(lines) == n + 1 and
         all(line.endswith(b'\r\n') for line in lines), 'CSV shape/dialect')
    rows = list(rd)
    need(len(rows) == n, 'CSV row count')
    for i, row in enumerate(rows, 1):
        need(None not in row and None not in row.values() and
             [row[k] for k in FIELDS[:5]] == [SERIES[g], str(r), str(i),
                 f'20261124:502:{g}:{r}:{i}', str(TRANSITIONS[g])] and
             row['status'] == 'OK' and row['error'] == '', 'row identity/status')
    return rows, lines


def qualify(args, index, ref, manifest, pins):
    need(index['schema'] == 1 and index['frozen_commit'] == FROZEN, 'index schema')
    entries = index['artifacts']
    need([(e['g'], e['r']) for e in entries] == KEYS and
         len({e['artifact_id'] for e in entries}) == 40 and
         len({e['job_id'] for e in entries}) == 40, '40 distinct indexed shards')
    need(all(e['run_id'] == source_run(e['g'], e['r']) and
             e['name'] == f"d05-{e['run_id']}-g{e['g']}-r{e['r']}" for e in entries), 'source run mapping')
    need({p.name for p in args.archives.glob('*.zip')} ==
         {f"{e['artifact_id']}.zip" for e in entries}, 'archive set incomplete/extra')
    package = args.checkpoint_package.read_bytes()
    need(sha(package) == PACKAGE_SHA, 'original package digest')
    with zipfile.ZipFile(io.BytesIO(package)) as z:
        zip_members(z)
        audit = parse(z.read('CAL01_CHECKPOINT_AUDIT.json'))
        checkpoint = z.read('VOY-REFLOW-CAL-01_CHECKPOINT.zip')
    need(sha(checkpoint) == CHECKPOINT_SHA, 'checkpoint digest')
    samples = {x['id']: x for x in audit['shards']}
    need(len(samples) == len(audit['shards']) and set(samples) <= {label(*k) for k in KEYS} and
         all(type(v['rows']) is int and 0 < v['rows'] <= 1000 for v in samples.values()) and
         sum(v['rows'] for v in samples.values()) == 850, 'historical control inventory')
    shards = []
    # No H1 or summary is parsed, and no gain is converted, during the structural pass.
    for e in entries:
        g, r = e['g'], e['r']
        key = label(g, r)
        raw = (args.archives / f"{e['artifact_id']}.zip").read_bytes()
        need(len(raw) == e['size'] and sha(raw) == e['archive_sha256'], 'archive digest/size')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            need(zip_members(z) == MEMBERS | {'manifest.json'}, 'artifact member set')
            m = parse(z.read('manifest.json'))
            files = {n: z.read(n) for n in MEMBERS}
        need(m['key'] == key and m['g'] == g and m['r'] == r and m['rows'] == 1000,
             'shard manifest identity')
        need(m['files'] == {n: sha(b) for n, b in files.items()}, 'member hashes')
        expected = samples.get(key, {})
        need(m['controls'] == expected.get('rows', 0) and m['epsilon'] == EPS and
             m['within'] is True and finite(m['max_delta']) and 0 <= m['max_delta'] <= EPS,
             'historical control manifest')
        rt = parse(files['runtime.json'])
        runtime_ok(rt, ref)
        need(str(rt['run']) == str(e['run_id']), 'runtime run identity')
        rows, lines = read_rows(files['reflow.csv'], g, r, 1000)
        stream = files['stream.sha256'].decode('ascii').strip()
        need(re.fullmatch('[0-9a-f]{64}', stream) is not None and
             (not expected or stream == expected['stream_sha256']), 'stream identity')
        shards.append(dict(entry=e, key=key, manifest=m, files=files, runtime=rt, rows=rows, lines=lines))
    need(len(shards) == 40 and len({v['seed'] for s in shards for v in s['rows']}) == 40000 and
         sum(s['manifest']['controls'] for s in shards) == 850, 'global completeness')
    # Historical bytes and numeric integrity are checked only after the complete structural pass.
    seen_rows, seen_h1 = set(), set()
    h = hashlib.sha256()
    with zipfile.ZipFile(io.BytesIO(checkpoint)) as z:
        zip_members(z)
        prefix = 'VOY-REFLOW-CAL-01/'
        receipt = parse(z.read(prefix + 'REMOTE_RECEIPT.json'))
        need(receipt['commit'] == FROZEN and receipt['remote_verified'] is True and
             receipt['manifest_sha256'] == pins['manifest_sha256'] and bool(receipt['observed_at_utc']),
             'checkpoint freeze receipt')
        for name, digest in manifest['local_files'].items():
            need(sha(z.read(prefix + name)) == digest, 'checkpoint frozen source')
        for name, digest in manifest['historical_files'].items():
            need(sha(z.read('reflow_execution/' + name)) == digest, 'checkpoint historical source')
        for s in shards:
            g, r = s['entry']['g'], s['entry']['r']
            key = s['key']
            if (g, r) == KEYS[0]:
                h.update(s['lines'][0])
            h.update(b''.join(s['lines'][1:]))
            expected = samples.get(key)
            old = []
            if expected:
                old_raw = z.read(prefix + 'output/' + key + '/reflow.csv')
                need(sha(old_raw) == expected['csv_sha256'], 'historical CSV digest')
                old, _ = read_rows(old_raw, g, r, expected['rows'])
            peak = 0.0
            gains = []
            for i, (row, line) in enumerate(zip(s['rows'], s['lines'][1:], strict=True)):
                value = float(row['gain_nats'])
                need(math.isfinite(value) and str(value) == row['gain_nats'], 'finite canonical gain')
                gains.append(value)
                seed = row['seed']
                if seed in ref['rows']:
                    need([sha(line), sha(struct.pack('>d', value))] == ref['rows'][seed], 'D05 row anchor')
                    seen_rows.add(seed)
                if i < len(old):
                    prior = old[i]
                    need(all(prior[k] == row[k] for k in FIELDS if k != 'gain_nats'), 'historical row identity')
                    old_value = float(prior['gain_nats'])
                    need(math.isfinite(old_value), 'historical gain finite')
                    peak = max(peak, abs(old_value - value))
            need(peak == s['manifest']['max_delta'] and peak <= EPS, 'recomputed historical envelope')
            if key in ref['h1']:
                need(sha(s['files']['H1.json']) == ref['h1'][key], 'D05 H1 anchor')
                seen_h1.add(key)
            s['gains'] = gains
    need(seen_rows == set(ref['rows']) and len(seen_rows) == 70 and
         seen_h1 == set(ref['h1']) and len(seen_h1) == 3, 'anchor coverage')
    # Validate all classifier inputs and summary schema only after global structural completeness.
    # No categories, frequencies or numerical values are emitted by qualification.
    for s in shards:
        h1_values(s)
        summary_values(s)
    dataset = h.hexdigest()
    bundle = sha(canonical(dict(dataset_sha256=dataset, artifacts=entries)))
    qualification = dict(status='TECHNICAL_PASS', pins=pins, rows=40000, shards=40, historical_controls=850,
                         dataset_sha256=dataset, bundle_sha256=bundle,
                         checkpoint_receipt={k: receipt[k] for k in ('commit', 'manifest_sha256', 'remote_verified', 'observed_at_utc')},
                         images=sorted({(s['runtime']['image'], s['runtime']['build']) for s in shards}))
    # JSON-compatible round-trip makes receipt comparison deterministic.
    return shards, parse(canonical(qualification))


def numerical_environment(args, ref, qualification):
    lock('numpy' not in sys.modules, 'numeric libraries imported before admission')
    lock(not sys.flags.optimize and platform.python_version() == '3.13.5' and
         platform.machine() == 'x86_64' and platform.system() == 'Linux' and
         {k: os.getenv(k) for k in ref['env']} == ref['env'] and
         'NPY_ENABLE_CPU_FEATURES' not in os.environ, 'aggregation environment')
    fields = {}
    def collect(entries):
        for entry in entries:
            fields[entry['field'].rstrip(':')] = entry.get('data')
            collect(entry.get('children', []))
    collect(json.loads(subprocess.check_output(['lscpu', '-J'], text=True))['lscpu'])
    lock(cpu_ok(fields, ref), 'aggregation CPU not admitted')
    import numpy as np
    import scipy.linalg.blas
    import sklearn.linear_model
    from numpy._core import _multiarray_umath as mu
    from threadpoolctl import threadpool_info
    lock((np.__version__, scipy.__version__, sklearn.__version__) == ('2.3.5', '1.17.0', '1.8.0'), 'numeric versions')
    pools = threadpool_info()
    loops = np.lib.introspect.opt_func_info()
    rt = dict(cpu=fields, env={k: os.getenv(k) for k in ref['env']},
              binaries={Path(p['filepath']).name: sha(Path(p['filepath']).read_bytes()) for p in pools},
              pools=pools, features=mu.__cpu_features__, targets=mu.__cpu_dispatch__,
              log64=loops['log']['dd']['current'], image=os.getenv('ImageOS'), build=os.getenv('ImageVersion'))
    runtime_ok(rt, ref)
    lock([rt['image'], rt['build']] in qualification['images'] and
         all('AVX512' not in v['current'].upper() for x in loops.values() for v in x.values()),
         'aggregation image/SIMD not verified')
    path = args.frozen / 'run.py'
    lock(sha(path.read_bytes()) == RUN_SHA, 'classifier bytes changed')
    spec = importlib.util.spec_from_file_location('cal01_frozen', path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)  # No gate(), init(), job() or main() is invoked.
    return np, model


def h1_values(s):
    h1 = parse(s['files']['H1.json'])
    ci = h1['conditional_ci95']
    need(finite(h1['gain']) and isinstance(ci, list) and len(ci) == 2 and
         all(finite(x) for x in ci) and ci[0] <= ci[1], 'invalid H1')
    return h1


def summary_values(s):
    v = parse(s['files']['summary.json'])
    g, r = s['entry']['g'], s['entry']['r']
    expected = {'H1_valid', 'G0', 'L0', 'mean', 'sd', 'rho', 'k', 'p',
                'percentiles', 'category', 'geometry', 'realization',
                'qo_frequency', 'qo_opening_frequency'}
    need(set(v) == expected and v['geometry'] == SERIES[g] and
         type(v['realization']) is int and v['realization'] == r and
         type(v['H1_valid']) is bool and type(v['k']) is int and 0 <= v['k'] <= 1000 and
         v['category'] in ('C', 'R', 'I'), 'summary schema/identity')
    need(all(finite(v[k]) for k in ('G0', 'L0', 'mean', 'sd', 'p',
                                  'qo_frequency', 'qo_opening_frequency')) and
         v['sd'] >= 0 and 0 <= v['p'] <= 1 and
         all(0 <= v[k] <= 1 for k in ('qo_frequency', 'qo_opening_frequency')) and
         (v['rho'] is None or finite(v['rho'])) and
         isinstance(v['percentiles'], list) and len(v['percentiles']) == 2 and
         all(finite(x) for x in v['percentiles']) and
         v['percentiles'][0] <= v['percentiles'][1], 'summary numeric schema')
    return v


def margin_audit(shards, qualification, np):
    # No classify(), category, frequency, k, p, G0 or rho is emitted in this phase.
    bounds = {'G0_zero': E_G0, 'L0_zero': E_L0, 'L0_quarter_G0': E_L0 + .25 * E_G0,
              'row_vs_G0': E_GAIN + E_G0, 'P97_5_zero': E_GAIN,
              'rho_quarter': E_GAIN + .25 * E_G0, 'rho_three_quarters': E_GAIN + .75 * E_G0,
              'adjacent_rank': 2 * E_GAIN}
    minima = dict.fromkeys(bounds, float('inf'))
    unresolved = []
    for s in shards:
        h1 = h1_values(s)
        g, l = h1['gain'], h1['conditional_ci95'][0]
        a = np.asarray(s['gains'], dtype=np.float64)
        need(a.shape == (1000,) and np.isfinite(a).all(), 'margin input size/finite')
        mean = float(a.mean())
        m = dict(G0_zero=abs(g), L0_zero=abs(l), L0_quarter_G0=abs(l - .25*g),
                 row_vs_G0=float(np.min(np.abs(a - g))),
                 P97_5_zero=abs(float(np.quantile(a, .975, method='linear'))),
                 rho_quarter=abs(mean - .25*g), rho_three_quarters=abs(mean - .75*g),
                 adjacent_rank=float(np.min(np.diff(np.sort(a)))))
        for name, distance in m.items():
            need(finite(distance), 'nonfinite audit margin')
            minima[name] = min(minima[name], distance)
            if distance <= bounds[name]:
                unresolved.append([s['key'], name])
        # Tail decision can be audited without publishing the tail count or p.
        k_min = int(np.count_nonzero(a - E_GAIN >= g + E_G0))
        k_max = int(np.count_nonzero(a + E_GAIN >= g - E_G0))
        if ((k_min + 1)/1001 <= .05) != ((k_max + 1)/1001 <= .05):
            unresolved.append([s['key'], 'tail_threshold'])
    return dict(status='MARGINS_ONLY', dataset_sha256=qualification['dataset_sha256'],
                bundle_sha256=qualification['bundle_sha256'], pins=qualification['pins'],
                empirical_epsilon=EPS, bounds=bounds, minimum_absolute_margins=minima,
                unresolved=unresolved, ties='indeterminate absent structural proof',
                quantile_value_bound=E_GAIN,
                caveat='Conservative empirical allocation; rank uncertainty is not quantile-value uncertainty. No automatic certification.')


def verdict(counts, h1, complete):
    if not complete:
        return 'INCOMPLETO'
    need(all(sum(counts[s].values()) == 20 and 0 <= h1[s] <= 20 for s in SERIES), 'decision denominator')
    if any(counts[s]['R'] for s in SERIES):
        return 'CONTROESEMPIO'
    if min(h1.values()) < 16:
        return 'NON QUALIFICATO'
    if all(counts[s]['C'] >= 16 for s in SERIES):
        return 'CONSERVAZIONE FREQUENTE'
    return 'INCONCLUDENTE'


def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    d = 1 + z*z/n
    center = (p + z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0., center-half), min(1., center+half)]


def describe(results):
    out = {}
    for series in SERIES:
        rows = [v for v in results if v['geometry'] == series]
        n = len(rows)
        counts = {c: sum(v['category'] == c for v in rows) for c in 'CRI'}
        h = sum(v['H1_valid'] for v in rows)
        out[series] = dict(n=n, counts=counts, H1_valid=h,
                           proportions={k: dict(value=v/n, wilson95=wilson(v, n)) for k, v in {**counts, 'H1': h}.items()},
                           mean_qo_frequency=sum(v['qo_frequency'] for v in rows)/n,
                           mean_qo_opening_frequency=sum(v['qo_opening_frequency'] for v in rows)/n,
                           recurrent_counterexample=counts['R'] >= 2)
    return out


def aggregate(shards, qualification, np, model):
    results = []
    for s in shards:
        h1 = h1_values(s)
        a = np.asarray(s['gains'], dtype=np.float64)
        need(a.shape == (1000,) and np.isfinite(a).all(), 'classification input size/finite')
        result = model.classify(h1, a)
        summary = summary_values(s)
        g, r = s['entry']['g'], s['entry']['r']
        need(result['category'] in {'C', 'R', 'I'} and summary['geometry'] == SERIES[g] and summary['realization'] == r and
             all(summary[k] == result[k] for k in result), 'canonical summary disagreement')
        result.update(geometry=SERIES[g], realization=r)
        for k in ('qo_frequency', 'qo_opening_frequency'):
            need(finite(summary[k]) and 0 <= summary[k] <= 1, 'invalid frequency')
            result[k] = summary[k]
        results.append(result)
    need(len(results) == 40, 'classification completeness')
    primary = describe(results)
    counts = {s: primary[s]['counts'] for s in SERIES}
    h = {s: primary[s]['H1_valid'] for s in SERIES}
    sensitivity = describe([v for v in results if (v['geometry'], v['realization']) != ('ZL3b', 4)])
    return dict(status='COMPLETE', verdict=verdict(counts, h, True), qualification=qualification,
                primary=primary, results=results, sensitivity_excluding_ZL3b_04=sensitivity,
                sensitivity_note='Post-hoc descriptive sensitivity; ZL3b n=19, IT2a n=20; no new decision threshold.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('phase', choices=['qualify', 'margins', 'aggregate'])
    p.add_argument('--frozen', type=Path, required=True)
    p.add_argument('--archives', type=Path, required=True)
    p.add_argument('--checkpoint-package', type=Path, required=True)
    p.add_argument('--index', type=Path, default=HERE/'INPUT_INDEX.json')
    p.add_argument('--reference', type=Path, default=HERE.parent/'reference.json')
    p.add_argument('--split-receipt', type=Path, default=HERE/'SPLIT_INTEGRITY_RECEIPT.json')
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--qualification', type=Path)
    p.add_argument('--margins', type=Path)
    p.add_argument('--authorization', type=Path)
    p.add_argument('--canonical-resolution-evidence', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise SystemExit('Refuse to overwrite output')
    code = 0
    try:
        index, ref, manifest, pins = sources(args)
        shards, q = qualify(args, index, ref, manifest, pins)
        if args.phase == 'qualify':
            report = q
        else:
            lock(args.qualification is not None and args.qualification.is_file() and read(args.qualification) == q, 'qualification receipt mismatch')
            np, model = numerical_environment(args, ref, q)
            margins = margin_audit(shards, q, np)
            if args.phase == 'margins':
                report = margins
            else:
                lock(args.margins is not None and args.margins.is_file() and read(args.margins) == margins, 'margin receipt mismatch')
                lock(args.authorization is not None and args.authorization.is_file(), 'final independent authorization missing')
                auth = read(args.authorization)
                lock(auth.get('approved') is True and auth.get('independent_review') is True and
                     isinstance(auth.get('reviewer'), str) and bool(auth['reviewer'].strip()) and auth.get('pins') == pins and
                     auth.get('qualification_sha256') == sha(args.qualification.read_bytes()) and
                     auth.get('margins_sha256') == sha(args.margins.read_bytes()) and
                     auth.get('ZL3b_04_qualified') is True, 'final review not approved for exact receipts')
                lock(not margins['unresolved'] or (auth.get('canonical_resolution_approved') is True and
                     args.canonical_resolution_evidence is not None and
                     args.canonical_resolution_evidence.is_file() and
                     auth.get('canonical_resolution_evidence_sha256') ==
                     sha(args.canonical_resolution_evidence.read_bytes())), 'insufficient margins not resolved')
                report = aggregate(shards, q, np, model)
    except Locked as exc:
        report, code = dict(status='AGGREGATION_LOCKED', reason=str(exc)), 2
    except Incomplete as exc:
        report, code = dict(status='INCOMPLETO', reason=str(exc)), 1
    except Exception as exc:
        # Do not leak scientific values or partial summaries in an exception report.
        report, code = dict(status='INCOMPLETO', reason=type(exc).__name__), 1
    with args.out.open('xb') as f:
        f.write(canonical(report))
    return code


if __name__ == '__main__':
    sys.exit(main())
