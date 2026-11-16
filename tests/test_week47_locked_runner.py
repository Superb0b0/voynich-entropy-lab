"""Synthetic-only checks for W47 locked null runner; no manuscript or holdout."""
import importlib.util,pathlib,unittest

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
if __name__=='__main__':unittest.main()
