"""Synthetic-only checks for W47 locked null runner; no manuscript or holdout."""
import importlib.util,json,os,pathlib,tempfile,unittest
from unittest.mock import patch

SOURCE=pathlib.Path(__file__).resolve().parents[1]/'research/week47-qo-decision/run_locked.py'
spec=importlib.util.spec_from_file_location('w47_null_runner_fixture',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def blocks(words,folios=20):
 return [('synthetic_'+str(i),tuple(words),tuple((j,j+1) for j in range(len(words)-1)))
         for i in range(folios)]

class FrozenNullSyntheticTests(unittest.TestCase):
 def test_identical_words_are_permutation_invariant(self):
  s=m.null_counts(blocks(['aa','aa','aa']),reps=70)
  self.assertEqual(s['OE'],1)
  self.assertEqual(s['observed'],40)
  self.assertEqual(s['expected'],40)
  self.assertEqual(s['p_depletion'],1)
  self.assertEqual(m.bootstrap(s,reps=70),[1,1])
 def test_shuffled_within_block_depletion(self):
  s=m.null_counts(blocks(['a','b','a','b']),reps=300)
  self.assertEqual(s['observed'],0)
  self.assertGreater(s['expected'],0)
  self.assertEqual(s['OE'],0)
  self.assertLess(s['p_depletion'],.01)
  self.assertEqual(m.bootstrap(s,reps=150),[0,0])
 def test_repeatable_random_process(self):
  self.assertEqual(m.null_counts(blocks(['a','a','b','b']),reps=45),
                   m.null_counts(blocks(['a','a','b','b']),reps=45))
 def test_no_eligible_pairs_fail_closed(self):
  with self.assertRaises(ValueError):
   m.null_counts([('f1',('a','a'),())])
 def test_zero_null_expectation_fail_closed(self):
  with self.assertRaises(ValueError):
   m.null_counts(blocks(['a','b','c']),reps=20)
 def test_minimum_cluster_gate(self):
  s=m.null_counts(blocks(['a','b','a','b'],folios=19),reps=30)
  with self.assertRaises(ValueError):m.bootstrap(s,reps=30)
 def test_quantile_linear_interpolation(self):
  self.assertEqual(m.quantile([0,10,20,30,40],.125),5.0)
 def test_explicit_four_outcomes(self):
  supported=dict(OE=.2,p_depletion=.0005,CI95=[.0,.7],physical_folios=50)
  falsified=dict(OE=1,p_depletion=.9,CI95=[.6,1.4],physical_folios=50)
  self.assertEqual(m.synthetic_classify(supported,supported),'SUPPORTED')
  self.assertEqual(m.synthetic_classify(falsified,falsified),'FALSIFIED')
  self.assertEqual(m.synthetic_classify(falsified,supported),'INCONCLUSIVE')

class AuthorizationGateTests(unittest.TestCase):
 def test_direct_local_launch_is_denied(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaisesRegex(m.AuthorizationError,'outside GitHub Actions'):
    m.require_preflight_authorization()

 def test_same_run_github_preflight_and_receipt_are_required(self):
  head='a'*40;run_id='12345'
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);event_path=root/'event.json';receipt_path=root/'receipt.json'
   event_path.write_text(json.dumps({'inputs':{'run_experiment':True}}))
   receipt={'schema_version':1,'decision':'READY_TO_RUN_EXPLORATORY_NULL_ONLY',
    'repository':m.GITHUB_REPO,'run_id':run_id,'head_sha':head,
    'workflow_path':'.github/workflows/week47-qo-gated.yml','review_commit':head,
    'reviewer':'IndependentReviewer','review_submitted_at':'2026-11-19T12:00:00+00:00',
    'gate_sha256':'1'*64,'runner_sha256':m.sha(pathlib.Path(m.__file__).read_bytes()),
    'preparer_sha256':m.sha((m.ROOT/'research/week47-qo-decision/training_preflight.py').read_bytes()),
    'protocol_sha256':m.PROTOCOL_SHA,'parser_sha256':m.RC12}
   receipt_path.write_text(json.dumps(receipt))
   env={'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'workflow_dispatch',
    'GITHUB_REPOSITORY':m.GITHUB_REPO,'GITHUB_REF_NAME':m.APPROVED_BRANCH,
    'GITHUB_EVENT_PATH':str(event_path),'GITHUB_RUN_ID':run_id,'GITHUB_SHA':head,
    'GITHUB_TOKEN':'synthetic-token','W47_PREFLIGHT_RECEIPT':str(receipt_path)}
   run={'status':'in_progress','event':'workflow_dispatch',
    'path':'.github/workflows/week47-qo-gated.yml','head_branch':m.APPROVED_BRANCH,
    'head_sha':head}
   jobs={'jobs':[{'name':name,'conclusion':'success'} for name in
    ('guard-tests','preflight','prepare-input','package-code')]+[
     {'name':'experiment','status':'in_progress'}]}
   with patch.dict(os.environ,env,clear=True),patch.object(m,'_github_json',side_effect=[run,jobs]):
    self.assertEqual(m.require_preflight_authorization(),receipt)

 def test_missing_preflight_job_blocks_runner(self):
  head='a'*40;run_id='12345'
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp);event=root/'event.json';receipt_path=root/'receipt.json'
   event.write_text(json.dumps({'inputs':{'run_experiment':'true'}}))
   receipt={'schema_version':1,'decision':'READY_TO_RUN_EXPLORATORY_NULL_ONLY',
    'repository':m.GITHUB_REPO,'run_id':run_id,'head_sha':head,
    'workflow_path':'.github/workflows/week47-qo-gated.yml','review_commit':head,
    'reviewer':'IndependentReviewer','review_submitted_at':'2026-11-19T12:00:00+00:00',
    'gate_sha256':'1'*64,'runner_sha256':m.sha(pathlib.Path(m.__file__).read_bytes()),
    'preparer_sha256':m.sha((m.ROOT/'research/week47-qo-decision/training_preflight.py').read_bytes()),
    'protocol_sha256':m.PROTOCOL_SHA,'parser_sha256':m.RC12}
   receipt_path.write_text(json.dumps(receipt))
   env={'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'workflow_dispatch',
    'GITHUB_REPOSITORY':m.GITHUB_REPO,'GITHUB_REF_NAME':m.APPROVED_BRANCH,
    'GITHUB_EVENT_PATH':str(event),'GITHUB_RUN_ID':run_id,'GITHUB_SHA':head,
    'GITHUB_TOKEN':'synthetic-token','W47_PREFLIGHT_RECEIPT':str(receipt_path)}
   run={'status':'in_progress','event':'workflow_dispatch',
    'path':'.github/workflows/week47-qo-gated.yml','head_branch':m.APPROVED_BRANCH,
    'head_sha':head}
   jobs={'jobs':[{'name':name,'conclusion':'success'} for name in
    ('guard-tests','prepare-input','package-code')]+[
     {'name':'experiment','status':'in_progress'}]}
   with patch.dict(os.environ,env,clear=True),patch.object(m,'_github_json',side_effect=[run,jobs]):
    with self.assertRaisesRegex(m.AuthorizationError,'preflight'):
     m.require_preflight_authorization()
if __name__=='__main__':unittest.main()
