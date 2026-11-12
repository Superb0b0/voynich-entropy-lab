#!/usr/bin/env python3
"""Final fixed ASTRO-11 control: bilateral Fisher and radial inscriptions baseline.
Comparison population: IVTFF @Ri/@Ro loci from all folios excluding f69v,
with f69r included. Circular-continuous @Cc is not an inscription unit.
No visual or paleographical analysis.
"""
from pathlib import Path
from collections import Counter
from scipy.stats import fisher_exact
import hashlib, json, random, re

INPUT=Path('/mnt/data/ZL3b-n(7).txt')
OUTPUT=Path('/mnt/data/ASTRO_11_FINAL_CONTROL.json')
EXPECTED='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
SEED=20261112
REPS=20000
raw=INPUT.read_bytes()
sha=hashlib.sha256(raw).hexdigest()
if sha!=EXPECTED: raise SystemExit('INPUT HASH MISMATCH '+sha)
loc_re=re.compile(r'^<(?P<folio>f[^.>,]+)\.(?P<number>\d+),(?P<type>@R[io])>\s*(?P<body>.*)$')
leading_anno=re.compile(r'^\s*(?:<![^>]*>|<%>|<\$>)*\s*')
rows=[]
for lineno,line in enumerate(raw.decode('utf-8-sig').splitlines(),1):
    m=loc_re.match(line)
    if not m:continue
    d=m.groupdict()
    body=leading_anno.sub('',d['body']).strip()
    if not body or body[0] not in 'abcdefghijklmnopqrstuvwxyz':
        raise SystemExit(f'INVALID INITIAL {lineno}: {body!r}')
    rows.append(dict(folio=d['folio'],locus=f"{d['folio']}.{d['number']}",kind=d['type'],text=body,initial=body[0]))
# Verify exact same f69r/f69v count and class as the prior parser.
a=[x for x in rows if x['folio']=='f69v' and x['kind']=='@Ri']
b=[x for x in rows if x['folio']=='f69r' and x['kind']=='@Ro']
assert len(a)==28 and len(b)==22,(len(a),len(b))
assert [int(x['locus'].split('.')[-1]) for x in a]==list(range(4,32))
assert [int(x['locus'].split('.')[-1]) for x in b]==list(range(21,43))
ao=sum(x['initial']=='o' for x in a)
bo=sum(x['initial']=='o' for x in b)
assert (ao,bo)==(20,7),(ao,bo)
other=[x for x in rows if x['folio']!='f69v']
assert len(other)>=28
others_o=sum(x['initial']=='o' for x in other)
# Fisher bilateral, descriptive comparison only (group length differs).
odds,fish_p=fisher_exact([[ao,len(a)-ao],[bo,len(b)-bo]],alternative='two-sided')
# Uniform without-replacement sampling of 28 inscription units from 114 comparison loci.
rng=random.Random(SEED)
sampled=[sum(x['initial']=='o' for x in rng.sample(other,len(a))) for _ in range(REPS)]
observed=ao
p_high=(1+sum(v>=observed for v in sampled))/(REPS+1)
sorted_s=sorted(sampled)
def q(p):return sorted_s[max(0,min(REPS-1,int(p*(REPS-1))))]
q025,q975=q(.025),q(.975)
positive=(fish_p<.05) and (observed>q975)
output={
 'verdict':'POSITIVO' if positive else 'NULLO',
 'input_sha256':sha,'seed':SEED,'n_draws':REPS,'sampling':'uniform without replacement; @Ri and @Ro; all folios except f69v; f69r included',
 'excluded':'@Cc continuous circular text; not the same unit as individual radial inscriptions',
 'n_f69v_Ri':len(a),'o_f69v_Ri':ao,'rate_f69v':ao/len(a),
 'n_f69r_Ro':len(b),'o_f69r_Ro':bo,'rate_f69r':bo/len(b),
 'fisher_two_sided_p':fish_p,'fisher_odds_ratio':odds,
 'n_radial_other':len(other),'other_o':others_o,'other_o_rate':others_o/len(other),
 'baseline_sample_n':len(a),'baseline_mean_count':sum(sampled)/REPS,
 'baseline_mean_rate':sum(sampled)/(REPS*len(a)),
 'baseline_empirical_95_interval_counts':[q025,q975],
 'baseline_empirical_95_interval_rate':[q025/len(a),q975/len(a)],
 'baseline_max_count':max(sampled),
 'baseline_tail_p_high':p_high,
 'baseline_counts':dict(sorted(Counter(sampled).items())),
 'comparison_by_folio':{f:{'n':len(l),'o':sum(x['initial']=='o' for x in l)} for f in sorted({x['folio'] for x in other}) for l in [[x for x in other if x['folio']==f]]},
 'criterion':'POSITIVO iff Fisher bilateral p<0.05 and observed o-count > empirical 97.5th percentile of other radial inscriptions',
 'status_comparison_f69r':'ESPLORATIVO',
 'status_cyclic_order':'NULLO (closed; not rerun)',
}
OUTPUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in output.items() if k!='baseline_counts'},indent=2,ensure_ascii=False))