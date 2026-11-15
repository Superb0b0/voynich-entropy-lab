import unittest
from exhaustive_bijections import enumerate_bijections,audit
class ExhaustiveTests(unittest.TestCase):
 def test_seven_symbols_complete(self):
  a=audit("abcdefg","ABCDEFG");self.assertEqual(a["enumerated"],5040);self.assertTrue(a["complete"])
 def test_unique(self):
  ks=list(enumerate_bijections("abc","XYZ"));self.assertEqual(len(ks),6);self.assertEqual(len({tuple(k[x] for x in "abc") for k in ks}),6)
 def test_reject_duplicate_alphabet(self):
  with self.assertRaises(ValueError):list(enumerate_bijections("aab","XYZ"))
 def test_reject_unequal(self):
  with self.assertRaises(ValueError):list(enumerate_bijections("ab","XYZ"))
if __name__=="__main__":unittest.main()
