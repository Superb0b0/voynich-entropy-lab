import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from anchor01_partition import partition

class PartitionTests(unittest.TestCase):
    def test_folio_isolation_and_repeatability(self):
        pages = ["f1r", "f1v", "f2r", "f3v", "f4r", "f5r", "f6v", "f7r"]
        a = partition(pages)
        b = partition(list(reversed(pages)))
        self.assertEqual(a, b)
        self.assertFalse(set(a["discovery_page_ids"]) & set(a["internal_test_page_ids"]))
        self.assertEqual(set(a["discovery_page_ids"]) | set(a["internal_test_page_ids"]), set(pages))
        for folio in ["f1", "f2", "f3", "f4", "f5", "f6", "f7"]:
            self.assertFalse(any(p.startswith(folio + "r") or p.startswith(folio + "v") for p in a["discovery_page_ids"]) and any(p.startswith(folio + "r") or p.startswith(folio + "v") for p in a["internal_test_page_ids"]))

    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            partition(["f1r"] * 5)

    def test_reject_insufficient_folios(self):
        with self.assertRaises(ValueError):
            partition(["f1r", "f1v", "f2r"])

    def test_reject_invalid_page(self):
        with self.assertRaises(ValueError):
            partition(["f1r", "f2r", "f3r", "f4r", "../secret"])

if __name__ == "__main__":
    unittest.main()
