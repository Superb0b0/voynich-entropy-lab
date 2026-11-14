#!/usr/bin/env python3
"""Synthetic fail-closed trace audit regression. No Voynich inputs."""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify_attempts", ROOT / "tools" / "verify_attempts.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class TraceAuditRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = pathlib.Path(self.tmp.name)
        self.attempt = root / "attempts" / "001-synthetic"
        self.attempt.mkdir(parents=True)
        self.target = root / "data" / "SYNTHETIC_ONLY.txt"
        self.target.parent.mkdir()
        self.target.touch()

    def test_absolute_protected_open_rejected(self):
        with self.assertRaises(RuntimeError):
            verify.audit_trace(f'123 open("{self.target}", O_RDONLY) = 3', self.attempt, {self.target})

    def test_relative_protected_open_rejected(self):
        with self.assertRaises(RuntimeError):
            verify.audit_trace('123 open("../../data/SYNTHETIC_ONLY.txt", O_RDONLY) = 3', self.attempt, {self.target})

    def test_chdir_then_relative_open_rejected(self):
        trace = ('123 chdir("../../data") = 0\n'
                 '123 openat(AT_FDCWD, "SYNTHETIC_ONLY.txt", O_RDONLY) = 3\n')
        with self.assertRaisesRegex(RuntimeError, "cwd change"):
            verify.audit_trace(trace, self.attempt, {self.target})

    def test_dirfd_relative_open_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "directory-fd"):
            verify.audit_trace('123 openat(3, "SYNTHETIC_ONLY.txt", O_RDONLY) = 4', self.attempt, {self.target})

    def test_safe_relative_open_allowed(self):
        verify.audit_trace('123 openat(AT_FDCWD, "notes.txt", O_RDONLY) = 3', self.attempt, {self.target})

if __name__ == "__main__":
    unittest.main()
