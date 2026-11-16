"""Synthetic-only tests for training input isolation. No manuscript data."""
import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'research/week47-qo-decision/training_preflight.py'
spec = importlib.util.spec_from_file_location('w47_training_slicer', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def source(*parts):
    return ('\n'.join(parts) + '\n').encode('utf-8')

class TestW47TrainingSlicer(unittest.TestCase):
    def test_excluded_page_cannot_contribute_any_lines(self):
        raw = source(
            '<f1r> <! $L=A>',
            '<f1r.1,*P0> safeone',
            '<f2r> <! $L=B>',
            '<f2r.1,*P0> forbidden',
            '<f3v> <! $L=A>',
            '<f3v.1,*P0> safethree')
        result, counts = mod.slice_pages(raw, {2})
        self.assertIn(b'safeone', result)
        self.assertIn(b'safethree', result)
        self.assertNotIn(b'forbidden', result)
        self.assertNotIn(b'<f2r>', result)
        self.assertEqual(counts['included_pages'], 2)
        self.assertEqual(counts['held_pages'], 1)
    def test_malformed_held_page_boundary_fails_closed(self):
        raw = source('<f1r> <! $L=A>', '<f1r.1,*P0> safe',
                     '<f2v> broken metadata', '<f2v.1,*P0> forbidden')
        with self.assertRaisesRegex(RuntimeError,'Malformed page boundary'):
            mod.slice_pages(raw, {2})
    def test_cross_page_locus_fails_closed(self):
        raw = source('<f1r> <! $L=A>', '<f1r.1,*P0> safe',
                     '<f2r.1,*P0> forbidden', '<f2r> <! $L=B>',
                     '<f2r.2,*P0> forbidden2')
        with self.assertRaisesRegex(RuntimeError,'Locus page mismatch'):
            mod.slice_pages(raw, {2})
    def test_header_without_metadata_fails_closed(self):
        raw = source('<f1v> <! $L=A>', '<f1v.1,*P0> safe',
                     '<f2r> $L=B', '<f2r.1,*P0> forbidden')
        with self.assertRaisesRegex(RuntimeError,'Malformed page boundary'):
            mod.slice_pages(raw, {2})
    def test_special_non_numeric_page_is_not_included(self):
        raw = source('<f1r> <! $L=A>', '<f1r.1,*P0> safe',
                     '<fRos> <! $L=A>', '<fRos.1,*P0> special',
                     '<f2r> <! $L=B>', '<f2r.1,*P0> forbidden')
        result,counts=mod.slice_pages(raw,{2})
        self.assertNotIn(b'special',result)
        self.assertNotIn(b'forbidden',result)
        self.assertEqual(counts['special_pages'],1)
    def test_unknown_partition_fails_if_no_held_page_seen(self):
        raw=source('<f1r> <! $L=A>', '<f1r.1,*P0> safe')
        with self.assertRaisesRegex(RuntimeError,'Missing or unverified'):
            mod.slice_pages(raw,{2})

if __name__ == '__main__':
    unittest.main()
