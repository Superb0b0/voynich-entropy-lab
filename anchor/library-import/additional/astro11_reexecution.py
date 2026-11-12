#!/usr/bin/env python3
"""ASTRO-11: ZL3b f69v @Ri vs f69r @Ro, fixed parser and baselines.
Reads only physical lines containing IVTFF loci. No image inspection.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, random, re
from scipy.stats import fisher_exact

SRC = Path('/mnt/data/ZL3b-n(7).txt')
EXPECTED = 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED:
    raise SystemExit(f'INPUT_HASH_MISMATCH: {sha}')

locus_pattern = re.compile(r'^<(?P<folio>f69[rv])\.(?P<num>\d+),(?P<typ>@R[io])>\s*(?:<![^>]*>)?\s*(?P<content>.*?)\s*$')
rows=[]
for physical_line, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
    m = locus_pattern.match(line)
    if m:
        d=m.groupdict(); d['physical_line']=physical_line; d['num']=int(d['num'])
        rows.append(d)
r=[x for x in rows if x['folio']=='f69r' and x['typ']=='@Ro']
v=[x for x in rows if x['folio']=='f69v' and x['typ']=='@Ri']
assert len(r)==22 and len(v)==28, (len(r),len(v))
assert [x['num'] for x in v]==list(range(4,32))
assert [x['num'] for x in r]==list(range(21,43))

# Raw leading EVA character; brackets later in word do not affect it.
def initial(x):
    return x['content'][0]
r_o=sum(initial(x)=='o' for x in r)
v_o=sum(initial(x)=='o' for x in v)
# A fixed one-sided hypothesis: o-initial enrichment in f69v.
odds,p_fisher=fisher_exact([[v_o,len(v)-v_o],[r_o,len(r)-r_o]],alternative='greater')

# Full exact word-string repeats; punctuation and uncertain characters are left unchanged.
v_counts=Counter(x['content'] for x in v)
# 28 cyclic positions, including last-to-first adjacency.
initials=[initial(x) for x in v]
observed=sum(initials[i]==initials[(i+1)%len(initials)] for i in range(len(initials)))
rng=random.Random(20261112)
reps=20000
surrogate=[]
for _ in range(reps):
    perm=initials.copy(); rng.shuffle(perm)
    surrogate.append(sum(perm[i]==perm[(i+1)%len(perm)] for i in range(len(perm))))
p_perm=(1+sum(x>=observed for x in surrogate))/(reps+1)
mean_null=sum(surrogate)/reps
# Quantiles and 95% empirical central interval
s=sorted(surrogate)
q=lambda x:s[min(reps-1,int(x*reps))]
report={
 'input':str(SRC),'input_sha256':sha,
 'parser':'^<f69r.NUM,@Ro> and ^<f69v.NUM,@Ri>; first ASCII EVA character, unchanged transcription; 28 cyclic positions',
 'n_f69r_Ro':len(r),'n_f69v_Ri':len(v),
 'f69r_o_initial':r_o,'f69v_o_initial':v_o,
 'odds_ratio':odds,'fisher_one_sided_p':p_fisher,
 'f69v_exact_unique_strings':len(v_counts),
 'f69v_duplicate_strings':{key:val for key,val in v_counts.items() if val>1},
 'f69v_okeod_loci':[f"f69v.{x['num']}" for x in v if x['content']=='okeod'],
 'observed_cyclic_equal_initial_neighbors':observed,
 'permutation_reps':reps,'permutation_seed':20261112,
 'permutation_mean':mean_null,'permutation_95pct_interval':[q(.025),q(.975)],'permutation_one_sided_p':p_perm,
 'f69v_initials':''.join(initials),
 'f69v_data':[{'locus':f"f69v.{x['num']}",'text':x['content']} for x in v],
 'f69r_data':[{'locus':f"f69r.{x['num']}",'text':x['content']} for x in r]
}
output=Path('/mnt/data/ASTRO_11_RIESCUZIONE.json')
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('f69v_data','f69r_data')},indent=2,ensure_ascii=False))