"""KEY-GATE-001 conservative result classifier. No holdout access."""
import json,math,sys
REQUIRED=('candidate_key_sha256','evaluator_sha256','language_model_sha256','holdout_sha256','holdout_isolation_audit_sha256','rival_generator_sha256','fitting_procedure_sha256','equivalence_audit_sha256','independent_reproduction_sha256','preregistration_commit')
def evaluate(r):
 if not isinstance(r,dict):return {'verdict':'NON VERIFICABILE','reason':'invalid record'}
 missing=[k for k in REQUIRED if not isinstance(r.get(k),str) or not r[k].strip()]
 if missing:return {'verdict':'NON VERIFICABILE','reason':'missing evidence','missing':missing}
 if r.get('audit_status')!='INDEPENDENTLY_VERIFIED' or r.get('rival_exchangeability') is not True or r.get('holdout_isolated') is not True or r.get('familywise_adjustment_verified') is not True:
  return {'verdict':'NON VERIFICABILE','reason':'audit, isolation, exchangeability or multiple-testing control not verified'}
 scores=r.get('rival_scores');candidate=r.get('candidate_score')
 if not isinstance(scores,list) or len(scores)<999:return {'verdict':'NON VERIFICABILE','reason':'fewer than 999 rivals'}
 if any(type(x) not in (int,float) or not math.isfinite(x) for x in [candidate,*scores]):return {'verdict':'NON VERIFICABILE','reason':'invalid scores'}
 cov=r.get('coverage');drop=r.get('dropped_fraction')
 if any(type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=1 for x in (cov,drop)):
  return {'verdict':'NON VERIFICABILE','reason':'invalid coverage'}
 p=(1+sum(x>=candidate for x in scores))/(len(scores)+1)
 if cov<.95 or drop>.01 or p>.001:return {'verdict':'FAIL','empirical_p':p}
 return {'verdict':'PASS','empirical_p':p,'note':'Statistical gate only, NOT decipherment'}
if __name__=='__main__':
 print(json.dumps(evaluate(json.load(open(sys.argv[1],encoding='utf-8'))),ensure_ascii=False))
