"""Independent structural auditor fixtures; contains no real Voynich text."""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("w47_second_structural",ROOT/"research/week47-qo-decision/parser_parity_independent.py")
s=importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class DummyCanonical:
    def parse_corpus(self,path,verify_source=False):
        return {"records":[
          dict(physical_line=2,locus_id="f1r.1",folio="f1r",line_index=1,tokens=["alpha"]),
          dict(physical_line=3,locus_id="f1r.2",folio="f1r",line_index=2,tokens=["beta"])
        ]}

class IndependentScannerTests(unittest.TestCase):
    def test_cleaner_removes_alternative_and_keeps_brace_content(self):
        tok,_=s.independent_tokens("alpha{beta}[x:y]zeta<$>")
        self.assertEqual(tok,["alphabetazeta"])
    def test_comments_are_removed_before_marker_selection(self):
        tok,body=s.independent_tokens("a<! correction >b<%>c<$>")
        self.assertEqual(tok,["a","b","c"])
        self.assertIn("<%>",body)
        self.assertNotIn("<! correction >",body)
    def test_true_adjacency_and_folio_delimitation(self):
        fake="<f1r> <! $L=A>\n<f1r.1,*P0> <%>alpha\n<f1r.2,*P0> beta<$>\n"
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)/"fake.ivtff"
            path.write_text(fake)
            x=s.scan(path,DummyCanonical())
        self.assertEqual(x["blocks"],1)
        self.assertEqual(x["adjacent_pairs"],1)
        self.assertEqual(x["in_blocks"],2)
        self.assertEqual(x["outside_blocks"],0)
        self.assertEqual(x["token_mismatches"],0)
    def test_unmatched_token_is_detected(self):
        fake="<f1r> <! $L=A>\n<f1r.1,*P0> <%>DIFFERENT\n<f1r.2,*P0> beta<$>\n"
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"fake.ivtff"
            p.write_text(fake)
            x=s.scan(p,DummyCanonical())
        self.assertEqual(x["token_mismatches"],1)

if __name__=="__main__":unittest.main()
