#!/usr/bin/env python3
"""W47 frozen exploratory null-only runner, NOT authorized until preflight PASS.
Never reads full originals or HOLDOUT. Exports aggregated data, no folio IDs or words.
"""
import datetime as dt,hashlib,importlib.util,json,math,os,pathlib,random,re,urllib.error,urllib.request
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[2]
SEED=20261116;REPS=10000;MIN_FOLIOS=20
RC12='8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'
PROTOCOL_SHA='22b4a8bc3951f6ccf06aeffffc9e45a016e33847ee51d3fe67f1d35751494f90'
GITHUB_REPO='Superb0b0/voynich-entropy-lab'
APPROVED_BRANCH='research/week47-qo-rivals-plan-20261116'
CUTOFF=dt.datetime.fromisoformat('2026-11-20T17:00:00+00:00')

class AuthorizationError(RuntimeError):pass

def _require(ok,message):
 if not ok:raise AuthorizationError(message)

def _github_json(url):
 token=os.environ.get('GITHUB_TOKEN')
 _require(bool(token),'GitHub Actions token missing; runner must follow preflight')
 req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json',
  'Authorization':f'Bearer {token}','X-GitHub-Api-Version':'2022-11-28'})
 try:
  with urllib.request.urlopen(req,timeout=20) as response:return json.loads(response.read())
 except (urllib.error.URLError,json.JSONDecodeError,OSError) as exc:
  raise AuthorizationError('Cannot verify the authorizing GitHub Actions run') from exc

def require_preflight_authorization():
 """Require a real same-run GitHub preflight and a matching approval receipt."""
 _require(os.environ.get('GITHUB_ACTIONS')=='true','Runner is disabled outside GitHub Actions')
 _require(os.environ.get('GITHUB_EVENT_NAME')=='workflow_dispatch',
          'Runner requires the gated manual workflow dispatch')
 _require(os.environ.get('GITHUB_REPOSITORY')==GITHUB_REPO,'Wrong repository context')
 _require(os.environ.get('GITHUB_REF_NAME')==APPROVED_BRANCH,'Wrong W47 branch context')
 try:
  with open(os.environ['GITHUB_EVENT_PATH'],encoding='utf-8') as f:event=json.load(f)
 except (KeyError,OSError,json.JSONDecodeError) as exc:
  raise AuthorizationError('GitHub dispatch event is unavailable') from exc
 run_input=(event.get('inputs') or {}).get('run_experiment')
 _require(run_input is True or run_input=='true','Manual run_experiment acknowledgement missing')
 run_id=os.environ.get('GITHUB_RUN_ID','');head=os.environ.get('GITHUB_SHA','')
 _require(run_id.isdigit() and re.fullmatch(r'[a-f0-9]{40}',head) is not None,
          'GitHub run identity is incomplete')
 receipt_path=os.environ.get('W47_PREFLIGHT_RECEIPT')
 _require(bool(receipt_path),'Preflight receipt missing')
 try:
  with open(receipt_path,encoding='utf-8') as f:receipt=json.load(f)
 except (OSError,json.JSONDecodeError) as exc:
  raise AuthorizationError('Preflight receipt is unreadable') from exc
 _require(receipt.get('schema_version')==1 and
          receipt.get('decision')=='READY_TO_RUN_EXPLORATORY_NULL_ONLY',
          'Preflight receipt does not authorize this runner')
 _require(receipt.get('repository')==GITHUB_REPO and
          str(receipt.get('run_id'))==run_id and receipt.get('head_sha')==head and
          receipt.get('workflow_path')=='.github/workflows/week47-qo-gated.yml',
          'Preflight receipt is not bound to this workflow run and commit')
 _require(receipt.get('review_commit')==head and
          receipt.get('reviewer','').casefold()!='Superb0b0'.casefold(),
          'Receipt lacks a non-author review of this exact commit')
 try:reviewed=dt.datetime.fromisoformat(receipt['review_submitted_at'].replace('Z','+00:00'))
 except (KeyError,TypeError,ValueError) as exc:
  raise AuthorizationError('Receipt review timestamp is invalid') from exc
 _require(reviewed.tzinfo is not None and reviewed<=CUTOFF,
          'Receipt approval was submitted after the W47 cutoff')
 _require(receipt.get('gate_sha256') and re.fullmatch(r'[a-f0-9]{64}',receipt['gate_sha256']),
          'Receipt gate manifest digest missing')
 _require(receipt.get('runner_sha256')==sha(pathlib.Path(__file__).read_bytes()),
          'Runner differs from the preflight-approved source')
 preparer_path=ROOT/'research/week47-qo-decision/training_preflight.py'
 _require(receipt.get('preparer_sha256')==sha(preparer_path.read_bytes()),
          'Preparer differs from the preflight-approved source')
 _require(receipt.get('protocol_sha256')==PROTOCOL_SHA and
          receipt.get('parser_sha256')==RC12,
          'Receipt protocol or parser digest mismatch')
 _require(sha((ROOT/'research/week47-qo-decision/PROTOCOL.json').read_bytes())==PROTOCOL_SHA,
          'Packaged protocol hash mismatch')
 _require(sha((ROOT/'experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py').read_bytes())==RC12,
          'Packaged parser hash mismatch')
 base=f'https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}'
 run=_github_json(base)
 _require(run.get('status')=='in_progress' and run.get('event')=='workflow_dispatch' and
          run.get('path')=='.github/workflows/week47-qo-gated.yml' and
          run.get('head_branch')==APPROVED_BRANCH and run.get('head_sha')==head,
          'GitHub API run metadata does not match the preflight receipt')
 jobs=_github_json(base+'/jobs?per_page=100').get('jobs',[])
 states={j.get('name'):j.get('conclusion') or j.get('status') for j in jobs}
 for name in ('guard-tests','preflight','prepare-input','package-code'):
  _require(states.get(name)=='success',f'Required same-run job did not pass: {name}')
 _require(states.get('experiment')=='in_progress','Runner is not executing in the gated experiment job')
 return receipt

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
 require_preflight_authorization()
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
