import json,tempfile,unittest
from pathlib import Path
from candidate_audit import audit
class CandidateAuditTests(unittest.TestCase):
 def test_partial_key_is_ineligible(self):
  p=Path(__file__).with_name('caspari_faccini_partial_key.json')
  r=audit(p);self.assertEqual(r['verdict'],'INELIGIBLE');self.assertTrue(r['holdout_access'] is False)
 def test_reports_ambiguity(self):
  p=Path(__file__).with_name('caspari_faccini_partial_key.json')
  r=audit(p);self.assertTrue(any('ambiguous mapping' in x for x in r['problems']))
 def test_reports_unformalized_rules(self):
  p=Path(__file__).with_name('caspari_faccini_partial_key.json')
  r=audit(p);self.assertTrue(any('rule not executable' in x for x in r['problems']))
if __name__=='__main__':unittest.main()
