#!/usr/bin/env python3
"""Regression for verifier's strace relative-path resolution, synthetic only.

Expected on current main: FAIL, because a chdir event is not tracked.
No real corpus or holdout is opened.
"""
import pathlib
import re
import tempfile
import unittest

PATH_RE = re.compile(r'(?:open|openat|openat2|readlink|readlinkat)\([^\n]*?"([^"\n]+)"')

def current_verifier_detects(trace, attempt_dir, protected):
    """Faithfully isolate the current verify_attempt trace path check."""
    for raw in PATH_RE.findall(trace):
        candidate = ((attempt_dir / raw).resolve() if not pathlib.Path(raw).is_absolute()
                     else pathlib.Path(raw).resolve())
        if candidate in protected:
            return True
    return False

class ChdirRegression(unittest.TestCase):
    def test_open_after_chdir_must_be_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            attempt = root / "attempts" / "001-synthetic"
            attempt.mkdir(parents=True)
            target = root / "data" / "SYNTHETIC_ONLY.txt"
            target.parent.mkdir()
            target.touch()
            # Real strace includes a PID prefix; this test does not parse
            # that prefix because the current verifier ignores it too.
            trace = ('123 chdir("../../data") = 0\n'
                     '123 openat(AT_FDCWD, "SYNTHETIC_ONLY.txt", O_RDONLY) = 3\n')
            self.assertTrue(
                current_verifier_detects(trace, attempt, {target.resolve()}),
                "FAIL CLOSED: verifier missed a protected relative open after chdir"
            )

if __name__ == "__main__":
    unittest.main()
