#!/usr/bin/env python3
"""Read-only canonical structural audit, never a scientific test/holdout evaluation.
Export ONLY aggregate counts and hashes; do not export folio names or text.
"""
import argparse, hashlib, importlib.util, json, re
from pathlib import Path
from collections import Counter

ZL3B='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
IT2A='7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5'
RC12='8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5'
TAGS={'*P0','*Pb','+P0','+P1','+Pb','+Pc','+Pr','=P0','=Pt','@P0','@P1','@Pb'}
HEADER=re.compile(r'^<([^>]+)>\s*(.*)$')
MARKERS={'<$>','<%>','<->','<~>','<d>','<@H=2>','<@H=3>'}

def sha(b):return hashlib.sha256(b).hexdigest()
def fingerprint(obj):return sha(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())
def historical_tokens(body):
 body=re.sub(r'<![^>]*>',' ',body)
 for m in MARKERS:body=body.replace(m,' ')
 body=re.sub(r'\[[^\[\]]*\]',' ',body).replace('{','').replace('}','')
 return re.findall(r'[A-Za-z]+',body.lower())
def census(path, original, full=True):
 raw=path.read_bytes();expected=ZL3B if full else IT2A
 if sha(raw)!=expected:raise ValueError('source_sha_mismatch:'+path.name)
 canon={}
 if full:
  parsed=original.parse_corpus(path,verify_source=True)
  canon={r['locus_id']:r['tokens'] for r in parsed['records']}
  if (len(canon),parsed['counts']['token_count'],parsed['counts']['type_count'])!=(4130,35492,6980):
   raise ValueError('canonical_4130_35492_6980_failed')
 lines=[];metadata={};curpage=None;diff=Counter()
 for n,s in enumerate(raw.decode('utf-8').splitlines(),1):
  m=HEADER.match(s)
  if not m:continue
  key,body=m.groups()
  if ',' not in key:
   if re.fullmatch(r'f(?:\d+[rv]\d*|Ros)',key):
    curpage=key;metadata[key]=dict(re.findall(r'\$([A-Z])=([^\s>]+)',body))
   continue
  loc,tag=key.split(',',1)
  if tag not in TAGS:continue
  page=loc.split('.')[0]
  if page!=curpage:diff['page_metadata_mismatch']+=1
  ts=historical_tokens(body)
  if full and ts!=canon.get(loc):diff['per_locus_token_mismatch']+=1
  try:ind=int(loc.rsplit('.',1)[-1])
  except (IndexError,ValueError):diff['non_numeric_locus']+=1;continue
  lines.append((n,page,loc,ind,'<%>' in body,'<$>' in body,ts[0] if ts else '',
                metadata.get(page,{}).get('L','UNKNOWN')))
 blocks=[];start=None;lastpage=None;row_to_block={};opened=closed=0
 for row in lines:
  n,page,loc,idx,op,cl,first,lang=row
  if page!=lastpage:
   if start is not None:diff['cross_page']+=1
   start=None;lastpage=page
  if op:
   opened+=1
   if start is not None:diff['nested']+=1
   start={'start':loc,'page':page,'start_physical':n,'rows':[]}
  if start is not None:start['rows'].append(row)
  if cl:
   closed+=1
   if start is None:diff['orphan_close']+=1
   else:
    start['end']=loc;start['end_physical']=n
    for r in start['rows']:row_to_block[r[0]]=len(blocks)
    blocks.append(start)
   start=None
 if start is not None:diff['unclosed_end']+=1
 # Aggregate-only diagnostics: classify exclusions without exposing page/locus IDs.
 outside=Counter()
 for row in lines:
  if row[0] not in row_to_block:
   outside['empty_first_word' if not row[6] else 'nonempty_first_word']+=1
   outside['has_open_marker' if row[4] else 'no_open_marker']+=1
   outside['has_close_marker' if row[5] else 'no_close_marker']+=1
 pairs=[];blocked=Counter();langbreak=Counter();boundary=[]
 for i,b in enumerate(blocks):
  boundary.append([b['page'],b['start'],b['end'],b['start_physical'],b['end_physical'],len(b['rows']),b['rows'][0][-1]])
  langbreak[b['rows'][0][-1]]+=1
  for l,r in zip(b['rows'],b['rows'][1:]):
   if r[3]==l[3]+1 and r[0]==l[0]+1:
    pairs.append([b['page'],b['start'],b['end'],l[2],r[2]]);blocked['strict_adjacent_pairs']+=1
   elif r[3]==l[3]+1:blocked['index_adjacent_nonphysical']+=1
   else:blocked['gap_or_out_of_order']+=1
 locus_digest=fingerprint([[row[2], row[0], row[3], sha(json.dumps(row[6]).encode())] for row in lines])
 return {
  'source_sha256':expected,'blocks':len(blocks),'start_markers':opened,'end_markers':closed,
  'P_loci':len(lines),'P_loci_in_blocks':len(row_to_block),'P_loci_outside_blocks':len(lines)-len(row_to_block),
  'types':parsed['counts']['type_count'] if full else None,
  'tokens':parsed['counts']['token_count'] if full else None,
  'block_boundary_manifest_sha256':fingerprint(boundary),
  'locus_manifest_sha256':locus_digest,
  'pair_eligibility_manifest_sha256':fingerprint(pairs),
  'block_ids':boundary, 'pair_ids':pairs, # REMOVED before external report
  'differences':dict(diff),'outside_block_categories':dict(outside),'adjacency_categories':dict(blocked),
  'blocks_by_currier':dict(langbreak)
 }

def main():
 a=argparse.ArgumentParser();a.add_argument('--zl3b',type=Path,required=True);a.add_argument('--it2a',type=Path,required=True)
 a.add_argument('--parser',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
 if sha(args.parser.read_bytes())!=RC12:raise SystemExit('FAIL CLOSED parser hash')
 spec=importlib.util.spec_from_file_location('rc12_w47',args.parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if mod.run_unit_tests():raise SystemExit('FAIL CLOSED parser unit tests')
 z=census(args.zl3b,mod,True);it=census(args.it2a,mod,False)
 # No folio IDs, first words or raw text are exported.
 z_blocks=z.pop('block_ids');it_blocks=it.pop('block_ids')
 z_pairs=z.pop('pair_ids');it_pairs=it.pop('pair_ids')
 zs=set(tuple(k[:3]) for k in z_blocks);its=set(tuple(k[:3]) for k in it_blocks)
 zp=set(tuple(k) for k in z_pairs);ip=set(tuple(k) for k in it_pairs)
 zmeta={tuple(k[:3]):k[-1] for k in z_blocks}
 imeta={tuple(k[:3]):k[-1] for k in it_blocks}
 discrepancies={'ZL3b_only_blocks':len(zs-its),'IT2a_only_blocks':len(its-zs),
               'common_blocks':len(zs&its),
               'common_blocks_with_different_currier':sum(zmeta[k]!=imeta[k] for k in zs&its),
               'ZL3b_only_pairs':len(zp-ip),'IT2a_only_pairs':len(ip-zp),
               'common_pairs_in_identical_blocks':len(zp&ip)}
 report={
  'audit_class':'STRUCTURAL_ONLY_NOT_SCIENTIFIC','canonical_parser_sha256':RC12,
  'ZL3b':z,'IT2a':it,'transcription_mapping':discrepancies,
  'ZL3b_structure_verified':z['blocks']==740 and z['start_markers']==740 and z['end_markers']==740 and
    z['P_loci']==4130 and not z['differences'],
  'IT2a_structural_pair_mapping_identical':not any(discrepancies.values()) and not it['differences'],
  'IT2a_token_matching_verified':False,
  'gate_ready':False,
  'why_not_ready':'Full-corpus structure only. IT2a correspondence and protected training isolation require independent verification.'}
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps({k:report[k] for k in ('ZL3b_structure_verified','IT2a_structural_pair_mapping_identical','IT2a_token_matching_verified','gate_ready','transcription_mapping')},sort_keys=True))
 if not report['ZL3b_structure_verified']:raise SystemExit(1)
if __name__=='__main__':main()
