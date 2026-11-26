"""Offline diagnostic integrity review; never load the full scientific matrix."""
import json
import math
import struct
from pathlib import Path
import diagnostic as d

def verified_sample(root):
    fingerprints = json.loads((root/'fingerprints.json').read_text())
    values = {}
    identity = {}
    keys = {f'{("ZL3b","IT2a")[g]}_{r:02d}' for g,r in d.IDS}
    d.require(set(fingerprints) == keys, 'H1 roster')
    import csv
    import io
    for (g,r), numbers in d.IDS.items():
        key = f'{("ZL3b","IT2a")[g]}_{r:02d}'
        folder = root/'recomputed'/key
        h1,rows = fingerprints[key]
        h1_raw = (folder/'H1.json').read_bytes()
        d.require(d.sha(h1_raw)==h1, 'H1 hash')
        identity[key] = h1
        values[key+'/H1'] = float(json.loads(h1_raw)['gain'])
        expected = [f'20261124:502:{g}:{r}:{i}' for i in numbers]
        d.require(set(rows)==set(expected), 'ID or seed')
        serialized = (folder/'reflow.csv').read_bytes().splitlines(True)
        parsed = list(csv.DictReader(io.StringIO(b''.join(serialized).decode(),newline='')))
        for seed,row,line in zip(expected,parsed,serialized[1:],strict=True):
            rh,gh,data = rows[seed]
            bits = struct.pack('>d',float(row['gain_nats']))
            d.require(row['seed']==seed and line.endswith(b'\r\n') and
                      (d.sha(line),d.sha(bits),bits.hex())==(rh,gh,data),'row integrity')
            identity[seed]=(rh,gh)
            values[seed]=struct.unpack('>d',bits)[0]
    d.require(all(map(math.isfinite,values.values())), 'non-finite sample')
    return identity,values

def compare(schedule, compatible, originals, historical_peak):
    # schedule supplied from all REST job IDs including failures; no survivor filtering.
    # originals is a sequence of maps for the 70 original IDs and three H1 gains.
    slots = set(range(1,21))
    d.require(set(schedule)==slots and len({j['id'] for j in schedule.values()})==20,
              'runner roster')
    expected_keys = {f'20261124:502:{g}:{r}:{i}' for (g,r),ids in d.IDS.items() for i in ids}
    expected_keys.update(f'{("ZL3b","IT2a")[g]}_{r:02d}/H1' for g,r in d.IDS)
    d.require(originals and set.union(*(set(v) for v in originals))==expected_keys,
              'original sample coverage')
    samples = list(originals)
    passed = []
    for index in range(8):
        config = f'D{index:02d}'
        reports = {}
        for slot,job in schedule.items():
            root = Path(job['folder'])/config
            try:
                status = json.loads((root/'status.json').read_text())
                d.require(len(status['cpu_model'])==4 and all(status['cpu_model']), 'CPU model')
                d.require(job['attempt']==1, 'run attempt')
                if status['status']=='verified':
                    identity,values = verified_sample(root)
                    d.require(set(values)==expected_keys, 'sample coverage')
                    status['fingerprints']=identity
                    samples.append(values)
                reports[slot]=status
            except (OSError,ValueError,TypeError,KeyError):
                reports[slot]={'status':'missing or invalid'}
        if index>=5 and d.review_candidate(reports,compatible[config]):
            passed.append(config)
    peak = historical_peak
    for key in expected_keys:
        paired = [s[key] for s in samples if key in s]
        d.require(all(map(math.isfinite,paired)), 'non-finite reference')
        if len(paired)>1:
            peak=max(peak,max(paired)-min(paired))
    return {'first_passing':next(iter(passed),None),'paired_peak':peak}
