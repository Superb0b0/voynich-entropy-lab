#!/usr/bin/env python3
"""KEY-GATE-001 safe preflight; no corpus or holdout access."""
import argparse,hashlib,json,math,pathlib,sys
KEY={'mapping','transcription_edition','segmentation','allowed_operations','training_provenance','null_budget'}
MODEL={'target_language','corpus_sha256','model_architecture','model_version','tokenizer','normalization','seed','hyperparameters','oov_policy'}
def load(p):
    v=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(v,dict): raise ValueError('Expected JSON object')
    return v
def check(v,fields):
    missing=sorted(fields-set(v))
    if missing: raise ValueError('Missing fields: '+','.join(missing))
def rank(candidate,rivals):
    if len(rivals)<999: raise ValueError('At least 999 rivals required')
    if not all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) for v in [candidate,*rivals]):
        raise ValueError('Nonfinite or invalid score')
    return (1+sum(v>=candidate for v in rivals))/(len(rivals)+1)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--key',type=pathlib.Path,required=True)
    p.add_argument('--model-manifest',type=pathlib.Path,required=True)
    p.add_argument('--scores',type=pathlib.Path)
    a=p.parse_args()
    key=load(a.key);model=load(a.model_manifest)
    check(key,KEY);check(model,MODEL)
    if not isinstance(key['mapping'],dict) or not key['mapping']: raise ValueError('Invalid mapping')
    if not all(isinstance(k,str) and k and isinstance(v,str) for k,v in key['mapping'].items()): raise ValueError('Invalid mapping entry')
    result={'status':'PREFLIGHT_ONLY','holdout_access':False,'decipherment':'NOT_VALIDATED',
      'key_sha256':hashlib.sha256(a.key.read_bytes()).hexdigest(),
      'model_manifest_sha256':hashlib.sha256(a.model_manifest.read_bytes()).hexdigest()}
    if a.scores:
        s=load(a.scores);check(s,{'candidate_score','rival_scores'})
        result['empirical_p']=rank(s['candidate_score'],s['rival_scores'])
        result['statistical_gate']='ELIGIBLE_FOR_FURTHER_AUDIT' if result['empirical_p']<=.001 else 'NOT_SUPPORTED'
        result['warning']='Unverified external scores: rival equivalence and decoded language not audited'
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,json.JSONDecodeError) as e:
        print('FAIL_CLOSED: '+str(e),file=sys.stderr);sys.exit(2)
