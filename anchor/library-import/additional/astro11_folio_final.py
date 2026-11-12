#!/usr/bin/env python3
"""ASTRO-11 final folio-based control. Strict predeclaration: ASTRO11_PREDECLARAZIONE.txt.
Unit: physical folio side; IVTFF panel suffixes merged; @Ri/@Ro, exact first EVA char.
No image reading, no external folio normalisation, no further variants.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, random, re, csv

INPUT=Path('/mnt/data/ZL3b-n(7).txt')
DECL=Path('/mnt/data/ASTRO11_PREDECLARAZIONE_FOLIO_FISICO.txt')
OUT=Path('/mnt/data/ASTRO11_FOLIO_FINAL.json')
CSV=Path('/mnt/data/ASTRO11_FOLIO_TABLE.csv')
EXPECTED='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
SEED=20261112
REPS=20000
sha=hashlib.sha256(INPUT.read_bytes()).hexdigest()
if sha != EXPECTED: raise SystemExit(f'HASH MISMATCH {sha}')
if not DECL.is_file():raise SystemExit('MISSING PREREG')
decl_sha=hashlib.sha256(DECL.read_bytes()).hexdigest()
regex=re.compile(r'^<(?P<folio>f[^.>,]+)\.(?P<number>\d+),(?P<kind>@R[io])>\s*(?P<body>.*)$')
leading=re.compile(r'^\s*(?:<![^>]*>|<%>|<\$>)*\s*')
all_rows=[]
for lineno,line in enumerate(INPUT.read_text(encoding='utf-8-sig').splitlines(),1):
    m=regex.match(line)
    if not m:continue
    d=m.groupdict()
    body=leading.sub('',d['body']).strip()
    if not body or not re.match(r'^[a-z]',body):
        raise SystemExit(f'UNSUPPORTED INITIAL line={lineno} {body!r}')
    all_rows.append({'folio':re.sub(r'(?<=[rv])[0-9]+$', '', d['folio']),'kind':d['kind'],'locus':f"{d['folio']}.{d['number']}",'initial':body[0]})
byfolio=defaultdict(list)
for row in all_rows:byfolio[row['folio']].append(row)
eligible={f:lst for f,lst in byfolio.items() if len(lst)>=8}
if 'f69v' not in eligible: verdict='INCONCLUSIVO'; p=None; rank=None; tied=None
elif len(eligible)<10:
    verdict='INCONCLUSIVO'; p=None
    obs=sum(x['initial']=='o' for x in eligible['f69v'])/len(eligible['f69v'])
    rank=1+sum(sum(x['initial']=='o' for x in lst)/len(lst)>obs for lst in eligible.values())
    tied=sum(sum(x['initial']=='o' for x in lst)/len(lst)>=obs for lst in eligible.values())
else:
    obs=sum(x['initial']=='o' for x in eligible['f69v'])/len(eligible['f69v'])
    tied=sum(sum(x['initial']=='o' for x in lst)/len(lst)>=obs for lst in eligible.values())
    p=tied/len(eligible)
    rank=1+sum(sum(x['initial']=='o' for x in lst)/len(lst)>obs for lst in eligible.values())
    verdict='POSITIVO' if p<0.05 else 'NULLO'
ordered=sorted(eligible.items(),key=lambda kv:(-sum(x['initial']=='o' for x in kv[1])/len(kv[1]),kv[0]))
table=[{'folio':f,'n':len(lst),'k':sum(x['initial']=='o' for x in lst),'fraction':sum(x['initial']=='o' for x in lst)/len(lst)} for f,lst in ordered]
with CSV.open('w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=['folio','n','k','fraction']);w.writeheader();w.writerows(table)
output={
 'verdict':verdict,'input_sha256':sha,'predeclaration_sha256':decl_sha,
 'unit':'physical folio side: IVTFF trailing panel suffixes merged (e.g. f68v1 and f68v3 to f68v)',
 'locus_types':['@Ri','@Ro'], 'eligible_min_n':8,
 'total_radial_loci':len(all_rows),'folios_with_radial_loci':len(byfolio),
 'n_eligible_folios':len(eligible),'n_excluded_folios':len(byfolio)-len(eligible),
 'table':table,'f69v':next((x for x in table if x['folio']=='f69v'),None),
 'rank_f69v':rank,'n_folios_fraction_at_least_f69v':tied,'p_folio_rank':p,
 'previous_result':'ESPLORATIVO',
 'seed':SEED if len(eligible)>=10 else None,
 'requested_permutations':REPS if len(eligible)>=10 else 0,
}
if len(eligible)>=10:
    # Folio-label permutations. Condition on each folio's complete bag of inscriptions.
    # Position of named folio 'f69v' is random in label permutations, preserving folio blocks.
    rng=random.Random(SEED)
    folios=list(sorted(eligible))
    fractions=[sum(x['initial']=='o' for x in eligible[f])/len(eligible[f]) for f in folios]
    observed=next(x['fraction'] for x in table if x['folio']=='f69v')
    ge=0
    null_values=[]
    for _ in range(REPS):
        # Permute labels, not the inscriptions: f69v assigned to one of the intact blocks
        # identically to a uniformly chosen member of the blocks.
        idx=rng.randrange(len(folios))
        val=fractions[idx]
        null_values.append(val)
        if val>=observed:ge+=1
    output['permutation_f69v_ge_count']=ge
    output['permutation_p_empirical']=(1+ge)/(REPS+1)
    output['permutation_baseline_fraction_mean']=sum(null_values)/REPS
    output['permutation_description']='shuffle folio labels among intact folio blocks; rank p is exact and invariant to label names'
OUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(output,indent=2,ensure_ascii=False))