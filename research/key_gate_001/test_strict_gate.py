import unittest
from strict_gate import REQUIRED,evaluate
def fixture():
 d={k:'synthetic-test-only' for k in REQUIRED}
 d.update(audit_status='INDEPENDENTLY_VERIFIED',rival_exchangeability=True,holdout_isolated=True,familywise_adjustment_verified=True,candidate_score=2,rival_scores=[1]*999,coverage=1,dropped_fraction=0)
 return d
class TestStrict(unittest.TestCase):
 def test_missing(self):
  d=fixture();del d['equivalence_audit_sha256'];self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
 def test_audit(self):
  d=fixture();d['audit_status']='PENDING';self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
 def test_exchangeability(self):
  d=fixture();d['rival_exchangeability']=False;self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
 def test_short(self):
  d=fixture();d['rival_scores']=[1]*998;self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
 def test_tie(self):
  d=fixture();d['rival_scores'][0]=2;self.assertEqual(evaluate(d)['verdict'],'FAIL')
 def test_coverage(self):
  d=fixture();d['coverage']=.94;self.assertEqual(evaluate(d)['verdict'],'FAIL')
 def test_familywise(self):
  d=fixture();d['familywise_adjustment_verified']=False;self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
 def test_synthetic_pass(self):self.assertEqual(evaluate(fixture())['verdict'],'PASS')
 def test_nan(self):
  d=fixture();d['candidate_score']=float('nan');self.assertEqual(evaluate(d)['verdict'],'NON VERIFICABILE')
if __name__=='__main__':unittest.main()
