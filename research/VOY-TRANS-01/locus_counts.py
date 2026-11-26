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
# Counts only; no predictions or scoring. Read only source lines referenced by admitted paragraphs.
import re
from collections import Counter, defaultdict
def collect(series):
    paths=list(base.rglob(series+'-n.txt'))
    expected={'ZL3b':'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc','IT2a':'7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5'}[series]
    paths=[p for p in paths if hashlib.sha256(p.read_bytes()).hexdigest()==expected]
    assert paths,series
    raw=paths[0].read_text(encoding='utf-8-sig').splitlines()
    # Full locus (including row type, if present); strip only transcriber suffix after semicolon.
    def locus(v,folio):
        n=v['physical_line']
        assert isinstance(n,int) and 1<=n<=len(raw)
        m=re.match(r'^\s*<([^>]+)>',raw[n-1])
        if not m: return None
        label=m.group(1).split(';')[0].strip()
        if not re.fullmatch(r'f\d+[rv]\d*\.[0-9]+(?:[.,][A-Za-z0-9]+)*',label): return None
        if label.split('.')[0]!=folio: return None
        return label
    counts=Counter(); entries=[]; missing=0; total=0
    for p in hist.paragraphs[series]:
        lines=p['lines']; sr=p['source_rows']; assert len(lines)==len(sr)
        ids=[locus(v,p['folio']) for v in sr]
        total+=len(ids); missing+=sum(k is None for k in ids)
        counts.update(k for k in ids if k is not None)
        if len(lines)<4: continue
        for i,(a,b) in enumerate(zip(lines,lines[1:]),1):
            if a and b: entries.append(((ids[i-1],ids[i]),(a[0],b[0]),p['folio'],sr[i]['physical_line']))
    rows=hist.raw_rows[series]
    assert len(entries)==len(rows)
    assert all(f==r['folio'] and n==r['source_row'] for (_,_,f,n),r in zip(entries,rows))
    ec=Counter(k for k,_,_,_ in entries)
    unique={k:v for k,v,_,_ in entries if None not in k and k[0]!=k[1] and ec[k]==1 and all(counts[x]==1 for x in k)}
    return counts,entries,unique,missing,total
data={s:collect(s) for s in model.SERIES}
a,b=model.SERIES
shared=set(data[a][0])&set(data[b][0])
unique_loci={k for k in shared if all(data[s][0][k]==1 for s in model.SERIES)}
common=set(data[a][2])&set(data[b][2])
byfolio=defaultdict(Counter)
for k in unique_loci: byfolio[k.split('.')[0]]['shared_unique_loci']+=1
for k in common: byfolio[k[0].split('.')[0]]['matched_transitions']+=1
out={}
for s,(counts,entries,unique,missing,total) in data.items():
    other=b if s==a else a
    groups=Counter(); leaves=defaultdict(Counter); reasons=Counter()
    for (k,v,f,n),r in zip(entries,hist.raw_rows[s]):
        if k in common:
            group='concordant' if v==data[other][2][k] else 'discordant'
        else:
            group='unalignable'
            reason='unparsed_endpoint' if None in k else 'nonunique_endpoint_or_pair' if k not in unique else 'absent_endpoint' if any(x not in data[other][0] for x in k) else 'ambiguous_other_endpoint' if any(x not in unique_loci for x in k) else 'no_matching_adjacent_transition'
            reasons[reason]+=1
        groups[group]+=1; leaves[group][r['leaf']]+=1; byfolio[f][s+'_'+group]+=1
    out[s]=dict(admitted_lines=total,unparsed_lines=missing,distinct_loci=len(counts),duplicate_loci=sum(v>1 for v in counts.values()),transitions=len(entries),groups=dict(groups),unalignable_reasons=dict(reasons),group_leaves={k:len(v) for k,v in leaves.items()},minimum_transitions_per_leaf={k:min(v.values()) for k,v in leaves.items()})
report=dict(status='COUNTS_ONLY',scope='admitted historical paragraph source lines only; exact locus label before semicolon; no offsets or fuzzy matching; adjacent admitted lines, not forced arithmetic successor',shared_loci=len(shared),shared_unique_loci=len(unique_loci),matched_transitions=len(common),folios_with_shared_unique_loci=sum(v['shared_unique_loci']>0 for v in byfolio.values()),folios_with_matched_transitions=sum(v['matched_transitions']>0 for v in byfolio.values()),results=out,by_folio={k:dict(v) for k,v in sorted(byfolio.items())})
(base.parent/'locus_counts.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='by_folio'},indent=2))
