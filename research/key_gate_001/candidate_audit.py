"""Validate candidate specification completeness; never decodes corpus."""
import json,sys
REQUIRED_RULES=('vowel_insertion','ending_truncation','detachable_o_apostrophe','qo_particle','contextual_exceptions')
def audit(path):
 d=json.load(open(path,encoding='utf-8')); problems=[]
 if d.get('schema')!='voynich-key-candidate/0.1':problems.append('unknown schema')
 entries=d.get('mapping',[])
 inputs=[x.get('input') for x in entries]
 if len(inputs)!=len(set(inputs)):problems.append('duplicate input units')
 for x in entries:
  if x.get('status','').startswith('AMBIGUOUS'):problems.append('ambiguous mapping: '+str(x.get('input')))
 for rule in REQUIRED_RULES:
  val=d.get('rules',{}).get(rule)
  if not isinstance(val,str) or val in ('NOT FORMALIZED','NOT SPECIFIED HERE'):problems.append('rule not executable: '+rule)
 if d.get('eligibility')!='ELIGIBLE':problems.append('candidate not explicitly eligible')
 return {'candidate_id':d.get('candidate_id'),'mapping_entries':len(entries),'problems':problems,'verdict':'INELIGIBLE' if problems else 'ELIGIBLE_FOR_PRECHECK_ONLY','holdout_access':False}
if __name__=='__main__':print(json.dumps(audit(sys.argv[1]),ensure_ascii=False,indent=2))
