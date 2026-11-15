import unittest
from evaluator import rank
class RankTests(unittest.TestCase):
 def test_all_lose(self):self.assertEqual(rank(2,[1]*999),.001)
 def test_tie(self):self.assertEqual(rank(2,[2]+[1]*998),.002)
 def test_all_win(self):self.assertEqual(rank(0,[1]*999),1.)
 def test_too_few(self):
  with self.assertRaises(ValueError):rank(1,[0]*998)
if __name__=='__main__':unittest.main()
