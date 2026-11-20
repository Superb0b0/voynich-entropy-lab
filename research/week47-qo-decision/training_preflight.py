#!/usr/bin/env python3
"""W47 training-only slicer and cross-transcription STRUCTURAL audit.
Prepare reads original source solely for page-header filtering and hashing.
Verify runs in a separate job with ONLY prepared authorized training inputs.
Never exports words, folio identifiers, protected partition IDs or test effects.
"""
import argparse,hashlib,importlib.util,json,re
from collections import Counter
from pathlib import Path

SOURCES={'ZL3b-n.txt':'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc',
         'IT2a-n.txt':'7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5'}
RC12='8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'
# Identity of the previously audited W47 training snapshots, NOT proof of
# independent protected-page provenance. Changes require explicit audit.
EXPECTED_TRAINING_SHA={
 'ZL3b-n.txt':'aba161811f3400c6810d43803f7a3ced5243ea29dd862eeb8c9b1ad144a9e38d',
 'IT2a-n.txt':'44891f0545382e51a09a607d1f62b88dbfb34acb44b4ca7db56001d54b0e1bd3'
}
PAGE=re.compile(r'^<(?P<page>f(?:\d+[rv]\d*|Ros))>[ \t]*<!')
ANY_PAGE_HEADER=re.compile(r'^<(?P<page>f[^>,]*)>')
ANY_LOCUS_HEADER=re.compile(r'^<(?P<locus>f[^>,]+),(?P<tag>[^>]+)>')
LOCUS=re.compile(r'^<(?P<locus>f(?:\d+[rv]\d*|Ros)\.\d+),(?P<tag>[^>]+)>[ \t]*(?P<body>.*)$')
LEAF=re.compile(r'^f(\d+)[rv]\d*$')
def sha(b):return hashlib.sha256(b).hexdigest()
def require_frozen_training_digest(name,digest):
 expected=EXPECTED_TRAINING_SHA.get(name)
 if expected is None or digest!=expected:
  raise RuntimeError('W47 snapshot digest differs from frozen technical baseline; independent provenance audit required')
 return digest

def module(path,label):
 spec=importlib.util.spec_from_file_location(label,path)
 if not spec or not spec.loader:raise RuntimeError('Missing source module')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def slice_pages(raw,held):
 # Reject ambiguous page transitions and cross-page locus records. A malformed
 # header must NEVER inherit the preceding page's inclusion flag.
 kept=[];included=None;active_page=None;stats=Counter()
 for s in raw.decode('utf-8').splitlines(keepends=True):
  h=ANY_PAGE_HEADER.match(s)
  m=PAGE.match(s)
  if h and not m:raise RuntimeError('Malformed page boundary: refusing ambiguous protected-page transition')
  if m:
   active_page=m.group('page')
   leaf=LEAF.fullmatch(active_page)
   included=bool(leaf and int(leaf.group(1)) not in held)
   stats['included_pages' if included else ('held_pages' if leaf else 'special_pages')]+=1
  locus=LOCUS.match(s)
  if ANY_LOCUS_HEADER.match(s) and not locus:
   raise RuntimeError('Malformed locus header: refusing ambiguous protected-page transition')
  if locus and locus.group('locus').split('.')[0]!=active_page:
   raise RuntimeError('Locus page mismatch: refusing ambiguous protected-page transition')
  if included:kept.append(s)
 if stats['included_pages']<1 or stats['held_pages']<1:
  raise RuntimeError('Missing or unverified training/held-page split')
 out=''.join(kept).encode('utf-8')
 # Check every included locus, not only included page headers.
 active_page=None
 for s in out.decode('utf-8').splitlines():
  m=PAGE.match(s)
  if m:
   active_page=m.group('page')
   leaf=LEAF.fullmatch(active_page)
   if not leaf or int(leaf.group(1)) in held:
    raise RuntimeError('Excluded page leaked into prepared snapshot')
  locus=LOCUS.match(s)
  if ANY_LOCUS_HEADER.match(s) and not locus:
   raise RuntimeError('Malformed locus in prepared snapshot')
  if locus and locus.group('locus').split('.')[0]!=active_page:
   raise RuntimeError('Nonmatching locus in prepared snapshot')
 return out,dict(stats)

def prepare(args):
 if not args.held_module:raise RuntimeError('Partition module required only in preparation')
 held=getattr(module(args.held_module,'partition').HELD,'copy')()
 if not isinstance(held,set) or not held or any(type(x) is not int for x in held):
  raise RuntimeError('Invalid authorized exclusion policy')
 target=args.root/'training-snapshot/data';target.mkdir(parents=True,exist_ok=True)
 report={'scope':'TRAINING_ONLY_TWO_TRANSCRIPTIONS','source':{},
         'protected_contents_exported':False,'scientific_test_executed':False,
         'partition_provenance':'requires independent audit; no scientific promotion'}
 for name,expected in SOURCES.items():
  raw=(args.root/'data'/name).read_bytes()
  if sha(raw)!=expected:raise RuntimeError('Full original SHA mismatch:'+name)
  subset,counts=slice_pages(raw,held)
  snapshot_digest=require_frozen_training_digest(name,sha(subset))
  (target/name).write_bytes(subset)
  report['source'][name]=dict(original_sha256=expected,training_sha256=snapshot_digest,
                               training_bytes=len(subset),**counts)
 output=args.root/'training-snapshot/report/input-manifest.json'
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('PASS: two training-only filtered inputs prepared, no protected text exported')

def blocks(path,parser):
 parsed=parser.parse_corpus(path,verify_source=False)
 lookup={r['locus_id'] for r in parsed['records']}
 meta={};curpage=None;opened=None;out={};issues=Counter()
 for n,s in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
  p=PAGE.match(s)
  if p:
   if opened is not None:issues['cross_page']+=1;opened=None
   curpage=p.group('page')
   meta[curpage]=dict(re.findall(r'\$([A-Z])=([^\s>]+)',s))
  m=LOCUS.match(s)
  if not m or m.group('tag') not in parser.ALLOWED_P_TAGS:continue
  locus=m.group('locus');page=locus.split('.')[0]
  if page!=curpage:issues['metadata_page_mismatch']+=1
  if '<%>' in m.group('body'):
   if opened is not None:issues['nested_start']+=1
   opened={'page':page,'start':locus,'rows':[]}
  if opened is not None:
   if locus not in lookup:issues['missing_canonical_tokenized_locus']+=1
   else:opened['rows'].append((locus,int(locus.rsplit('.',1)[-1]),n))
  if '<$>' in m.group('body'):
   if opened is None:issues['orphan_end']+=1
   else:
    key=(opened['page'],opened['start'],locus)
    if key in out:issues['duplicate_block']+=1
    pairs=frozenset((a[0],b[0]) for a,b in zip(opened['rows'],opened['rows'][1:])
                     if b[1]==a[1]+1 and b[2]==a[2]+1)
    out[key]=dict(shape=tuple(r[0] for r in opened['rows']),pairs=pairs,
                  currier=meta.get(page,{}).get('L','UNKNOWN'))
   opened=None
 if opened is not None:issues['unclosed_end']+=1
 if issues:raise RuntimeError('Training structural failure (aggregate only):'+json.dumps(issues))
 return out,parsed

def verify(args):
 manifest=json.loads((args.root/'training-snapshot/report/input-manifest.json').read_text())
 if manifest.get('scope')!='TRAINING_ONLY_TWO_TRANSCRIPTIONS':
  raise RuntimeError('Wrong isolation scope')
 if not args.parser or sha(args.parser.read_bytes())!=RC12:
  raise RuntimeError('Canonical parser source mismatch')
 parser=module(args.parser,'rc12')
 if parser.run_unit_tests():raise RuntimeError('Canonical parser failed selftests')
 table={};allblocks={}
 for name,source_hash in SOURCES.items():
  info=manifest['source'][name]
  if info['original_sha256']!=source_hash:raise RuntimeError('Original provenance mismatch')
  local=args.root/'training-snapshot/data'/name
  if sha(local.read_bytes())!=info['training_sha256']:
   raise RuntimeError('Training artifact integrity mismatch')
  require_frozen_training_digest(name,info['training_sha256'])
  b,parsed=blocks(local,parser);allblocks[name]=b
  table[name]=dict(training_sha256=info['training_sha256'],
                   P_loci=parsed['counts']['canonical_loci'],
                   token_count=parsed['counts']['token_count'],
                   blocks=len(b))
 left,right=allblocks.values();common=set(left)&set(right)
 lang={k for k in common if left[k]['currier']==right[k]['currier']}
 exact={k for k in lang if left[k]['currier'] in ('A','B')
        and left[k]['shape']==right[k]['shape']
        and left[k]['pairs']==right[k]['pairs']}
 shared_pairs=sum(len(left[k]['pairs']) for k in exact)
 folios={re.match(r'^(f\d+)[rv]',k[0]).group(1) for k in exact
         if re.match(r'^f\d+[rv]',k[0])}
 result={'status':'TRAINING_STRUCTURE_ONLY_NOT_SCIENTIFIC',
  'inputs':table,'common_blocks':len(common),
  'common_blocks_with_matching_currier':len(lang),
  'exact_matching_AB_blocks':len(exact),
  'exact_matching_pairs':shared_pairs,
  'physical_folios_with_matched_blocks':len(folios),
  'gate_ready':False,'output_contains_words':False,
  'output_contains_partition_or_folio_ids':False,
  'limitations':['No scientific test performed','Additional independent partition provenance review needed',
                 'IT2a is the same manuscript, not independent evidence',
                 'Locked runner not yet independently audited']}
 target=args.root/'research-output/w47-training-shape.json'
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('common_blocks','common_blocks_with_matching_currier',
         'exact_matching_AB_blocks','exact_matching_pairs','physical_folios_with_matched_blocks','gate_ready')},sort_keys=True))
 if len(exact)<1 or shared_pairs<1:raise RuntimeError('No comparable training geometry')

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','verify'])
 p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--held-module',type=Path)
 p.add_argument('--parser',type=Path);a=p.parse_args()
 (prepare if a.action=='prepare' else verify)(a)
if __name__=='__main__':main()
