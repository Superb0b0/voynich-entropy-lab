"""W47 selector provenance audit: fake folios only, never real partition."""
import importlib.util
import pathlib
import unittest

HERE=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("w47_policy_provenance",HERE/"research/week47-qo-decision/partition_policy_provenance.py")
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class TestPolicyProvenance(unittest.TestCase):
    def test_deterministic_stratified_selection(self):
        source="\n".join(
          f"<f{i}r> <! $L={'A' if i<6 else 'B'}>" for i in range(1,11)
        ).encode()
        x,n,s=p.derive_partition(source,20261114,.2)
        y,n2,s2=p.derive_partition(source,20261114,.2)
        self.assertEqual(x,y)
        self.assertEqual(n,10)
        self.assertEqual(s,2)
        self.assertEqual(len(x),2)
    def test_page_language_tie_uses_original_order(self):
        raw=b"<f1r> <! $L=B>\n<f1v> <! $L=A>\n<f2r> <! $L=B>\n<f3r> <! $L=A>\n"
        x,n,s=p.derive_partition(raw,20261114,.2)
        self.assertEqual(n,3)
        self.assertEqual(s,2)
        self.assertEqual(len(x),2)
    def test_bad_parameters_rejected(self):
        for seed,fraction in ((True,.2),(20261114,0),(20261114,1),(20261114,-.1)):
            with self.subTest(seed=seed,fraction=fraction):
                with self.assertRaisesRegex(RuntimeError,"Invalid selector"):
                    p.derive_partition(b"<f1r> <! $L=A>",seed,fraction)
    def test_source_is_parsed_not_executed(self):
        s='SEED=7\nHELD={5,6}\n'
        self.assertEqual(p.load_literal_assignment(s,'SEED'),7)
        self.assertEqual(p.load_literal_assignment(s,'HELD'),{5,6})
        with self.assertRaises(ValueError):
            p.load_literal_assignment('HELD=set(range(1,20))','HELD')
    def test_duplicate_literal_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"ambiguous"):
            p.load_literal_assignment('HELD={1}\nHELD={2}\n','HELD')
    def test_no_page_headers_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"No recognized"):
            p.derive_partition(b"NO PAGES",20261114,.2)

if __name__=='__main__':
    unittest.main()
