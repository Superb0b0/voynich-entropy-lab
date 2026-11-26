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
# Counts only. No predict(), score(), loss or gain.
from collections import Counter, defaultdict
def collect(series):
    entries=[]
    physical=Counter()
    for p in hist.paragraphs[series]:
        lines=p['lines']; sr=p['source_rows']; assert len(lines)==len(sr)
        for v in sr:
            physical[(p['folio'],v['physical_line'])]+=1
        if len(lines)<4: continue
        for i,(a,b) in enumerate(zip(lines,lines[1:]),1):
            if not a or not b: continue
            key=(p['folio'],sr[i-1]['physical_line'],sr[i]['physical_line'])
            entries.append((key,(a[0],b[0])))
    rows=hist.raw_rows[series]
    assert len(entries)==len(rows)
    assert all(k[0]==r['folio'] and k[2]==r['source_row'] for (k,_),r in zip(entries,rows))
    return entries,physical
data={s:collect(s) for s in model.SERIES}
maps={}
for s,(entries,physical) in data.items():
    counts=Counter(k for k,_ in entries)
    maps[s]={k:v for k,v in entries if counts[k]==1 and k[1]!=k[2] and physical[(k[0],k[1])]==1 and physical[(k[0],k[2])]==1}
common=set.intersection(*(set(m) for m in maps.values()))
a,b=model.SERIES
groups={k:('concordant' if maps[a][k]==maps[b][k] else 'discordant') for k in common}
out={}
for s,(entries,physical) in data.items():
    c=Counter(); leaves=defaultdict(set)
    for (k,_),r in zip(entries,hist.raw_rows[s]):
        label=groups[k] if k in common and k in maps[s] else 'unalignable'
        c[label]+=1; leaves[label].add(r['leaf'])
    out[s]=dict(total=len(entries),physical_ids=len(physical),ambiguous_physical_ids=sum(v>1 for v in physical.values()),ambiguous_transition_rows=sum(k not in maps[s] for k,_ in entries),unique_candidate_transitions=len(maps[s]),group_counts=dict(c),group_leaves={k:len(v) for k,v in leaves.items()})
report=dict(status='COUNTS_ONLY',scope='exact folio and both physical_line IDs, unique endpoints in both corpora; exact first normalized token at both endpoints; no fuzzy matches',caveat='Shared ID labels are candidate matches, not independently verified image coordinates; normalized token agreement does not resolve original uncertainty markers',matched_pairs=len(common),results=out)
(base.parent/'alignment_counts.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
