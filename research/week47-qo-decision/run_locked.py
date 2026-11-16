#!/usr/bin/env python3
"""W47 frozen exploratory null-only runner, NOT authorized until preflight PASS.
Never reads full originals or HOLDOUT. Exports aggregated data, no folio IDs or words.
"""
import hashlib,importlib.util,json,math,pathlib,random,re
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[2]
SEED=20261116;REPS=10000;MIN_FOLIOS=20
RC12='8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'
PROTOCOL_SHA='22b4a8bc3951f6ccf06aeffffc9e45a016e33847ee51d3fe67f1d35751494f90'

def sha(b):return hashlib.sha256(b).hexdigest()
def module(path,label):
 spec=importlib.util.spec_from_file_location(label,path)
 if not spec or not spec.loader:raise RuntimeError('Missing trusted source')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def quantile(seq,p):
 s=sorted(seq)
 if not s:raise RuntimeError('Empty bootstrap')
 v=(len(s)-1)*p;lo=math.floor(v);hi=math.ceil(v)
 return s[lo]+(v-lo)*(s[hi]-s[lo])

def null_counts(blocks,reps=REPS,seed=SEED):
 """Synthetic-compatible rows: (physical_folio, tuple(words), tuple((i,j),...))."""
 if reps<1:raise ValueError('Invalid permutations count')
 rng=random.Random(seed);observed=Counter();expected_sum=Counter();total=0;pairs=0;null=[]
 for folio,words,edges in blocks:
  if not edges:continue
  if len(words)<2 or any(i<0 or j<0 or i>=len(words) or j>=len(words) or i==j for i,j in edges):
   raise ValueError('Invalid adjacency in block')
  c=sum(words[i]==words[j] for i,j in edges)
  observed[folio]+=c;total+=c;pairs+=len(edges)
 if pairs==0:raise ValueError('No eligible adjacent rows')
 for _ in range(reps):
  c=0
  for folio,words,edges in blocks:
   if not edges:continue
   w=list(words);rng.shuffle(w)
   v=sum(w[i]==w[j] for i,j in edges)
   c+=v;expected_sum[folio]+=v
  null.append(c)
 expected=sum(null)/reps
 if expected<=0:raise ValueError('Expected repetition count is zero')
 return dict(observed=total,expected=expected,pairs=pairs,OE=total/expected,
             p_depletion=(1+sum(c<=total for c in null))/(reps+1),
             observed_by_folio=observed,
             expected_by_folio={f:expected_sum[f]/reps for f in observed})

def bootstrap(stat,reps=REPS,seed=SEED):
 obs=stat['observed_by_folio'];exp=stat['expected_by_folio']
 folios=sorted(obs)
 if len(folios)<MIN_FOLIOS:raise ValueError('Fewer than 20 contributing folios')
 rng=random.Random(seed);s=[]
 for _ in range(reps):
  selected=[folios[rng.randrange(len(folios))] for __ in folios]
  denominator=sum(exp[f] for f in selected)
  if denominator<=0:raise ValueError('Zero resampled denominator')
  s.append(sum(obs[f] for f in selected)/denominator)
 return [quantile(s,.025),quantile(s,.975)]

def synthetic_classify(a,b):
 supported=lambda x:(x['OE']<=.5 and x['p_depletion']<=.01 and
                     x['CI95'][1]<1 and x['physical_folios']>=MIN_FOLIOS)
 falsified=lambda x:x['CI95'][0]>.5
 if supported(a) and supported(b):return 'SUPPORTED'
 if falsified(a) and falsified(b):return 'FALSIFIED'
 return 'INCONCLUSIVE'

def prepare():
 if (ROOT/'HOLDOUT.md').exists() or any((ROOT/'data'/name).exists() for name in ('ZL3b-n.txt','IT2a-n.txt')):
  raise RuntimeError('Original or protected data present in analysis workspace')
 p=ROOT/'research/week47-qo-decision/PROTOCOL.json'
 if sha(p.read_bytes())!=PROTOCOL_SHA:raise RuntimeError('Frozen protocol changed')
 proto=json.loads(p.read_text())
 if proto['question_type']!='NULL_ONLY' or proto['scope']['endpoint']!='EXACT_FIRST_WORD_REPETITION':
  raise RuntimeError('Wrong frozen hypothesis')
 original=ROOT/'experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py'
 if sha(original.read_bytes())!=RC12:raise RuntimeError('Parser is not canonical RC1.2')
 parser=module(original,'w47_can_parser')
 if parser.run_unit_tests():raise RuntimeError('Canonical parser regression failure')
 filtercode=module(ROOT/'research/week47-qo-decision/training_preflight.py','w47_input_verifier')
 manifest=json.loads((ROOT/'training-snapshot/report/input-manifest.json').read_text())
 if manifest.get('scope')!='TRAINING_ONLY_TWO_TRANSCRIPTIONS':raise RuntimeError('Unapproved population')
 named=('ZL3b-n.txt','IT2a-n.txt')
 blocks={};words={};provenance={}
 for name in named:
  path=ROOT/'training-snapshot/data'/name
  h=sha(path.read_bytes())
  if h!=manifest['source'][name]['training_sha256']:raise RuntimeError('Snapshot SHA mismatch')
  b,records=filtercode.blocks(path,parser)
  blocks[name]=b
  words[name]={r['locus_id']:r['tokens'][0] for r in records['records']}
  provenance[name]={'training_sha256':h,'P_loci':records['counts']['canonical_loci']}
 a,b=blocks[named[0]],blocks[named[1]]
 common=[]
 for key in sorted(set(a)&set(b)):
  x,y=a[key],b[key]
  if x['currier'] in ('A','B') and x['currier']==y['currier'] and x['shape']==y['shape'] and x['pairs']==y['pairs']:
   common.append((key,x))
 if not common:raise RuntimeError('No matching blocks')
 outputs={name:[] for name in named};contributing=set();npairs=0
 for (page,start,end),block in common:
  m=re.match(r'^(f\d+)[rv]',page)
  if not m:raise RuntimeError('Nonnumeric folio is not in approved training')
  folio=m.group(1)
  indices={locus:i for i,locus in enumerate(block['shape'])}
  edges=tuple(sorted((indices[l],indices[r]) for l,r in block['pairs']))
  if any(j!=i+1 for i,j in edges):raise RuntimeError('Nonconsecutive pair present')
  npairs+=len(edges)
  if edges:contributing.add(folio)
  for name in named:
   outputs[name].append((folio,tuple(words[name][l] for l in block['shape']),edges))
 if len(contributing)<MIN_FOLIOS:raise RuntimeError('Insufficient physical folios')
 return outputs,dict(common_AB_blocks=len(common),comparable_pairs=npairs,
                     contributing_physical_folios=len(contributing),inputs=provenance)

def run():
 data,cohort=prepare();results={}
 for name,rows in data.items():
  st=null_counts(rows);ci=bootstrap(st)
  results[name]=dict(observed=st['observed'],expected=st['expected'],
                     pairs=st['pairs'],OE=st['OE'],p_depletion=st['p_depletion'],
                     CI95=ci,physical_folios=len(st['observed_by_folio']))
 verdict=synthetic_classify(results['ZL3b-n.txt'],results['IT2a-n.txt'])
 return dict(study_id='W47-EXACT-FIRSTWORD-NULL-01',
             verdict=verdict,scientific_status='EXPLORATORY_NOT_INDEPENDENT',
             frozen_protocol_sha256=PROTOCOL_SHA,canonical_parser_sha256=RC12,
             seed=SEED,permutation_reps=REPS,folio_bootstrap_reps=REPS,
             cohort=cohort,results=results,
             limitations=['Same already-explored manuscript','Not a generator rival test',
                          'IT2a is not an independent manuscript','No folio, hand or quire independence is established'])

def main():
 first=run();second=run()
 a=json.dumps(first,sort_keys=True,indent=2)+'\n'
 if a!=json.dumps(second,sort_keys=True,indent=2)+'\n':
  raise RuntimeError('Deterministic replay mismatch')
 target=ROOT/'research-output';target.mkdir(exist_ok=True)
 (target/'w47-null-only-result.json').write_text(a)
 print(json.dumps(dict(study_id=first['study_id'],verdict=first['verdict'],
                       scientific_status=first['scientific_status'],
                       raw_words_exported=False),sort_keys=True))
if __name__=='__main__':main()
