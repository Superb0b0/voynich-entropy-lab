# Attempt 001: archival reproducibility blocker

Date: 2026-11-15. Status: **NON VERIFICATO / BLOCKED**, not REPRODUCED or VALIDATED.

The general GitHub Actions verifier (run 43735980414, commit ded8c510f48781ee0fe434c49255f60e2f0782c8) successfully passed the previously blocking one-page inventory discrepancy and then stopped at `attempts/001-paragraph-header-key` with: `missing attempt.yml; cannot infer execution contract`.

The committed `attempts/001-paragraph-header-key/results.json` exists and records configuration and results. Direct checks did not locate `attempts/001-paragraph-header-key/run.sh`, `protocol.md`, or `README.md` on the research branch. These observations do not prove the original execution code is absent elsewhere in history.

**Do not** synthesize an `attempt.yml` or `run.sh` from the numbers in `results.json`. Do not exclude 001 from the general verifier or relabel CI as green. The archive must retain its historical result and its unverified status.

Next actions: (1) recover original source and invocation from documented provenance, if available; (2) compare source hashes and required inputs against the archive; (3) implement a holdout-safe replay with the original declared seed, outputs, and tolerance, preserving original result; (4) run full CI; (5) if original code is unavailable, formally classify the attempt as **NON REPRODUCIBILE** and create a separate *new* experiment with a new ID, not a retroactive replay.

The ANCHOR-02 independent confirmation remains **LOCKED_PENDING_GATE**. The protected holdout must remain sealed until full CI, independent parser review, and prospective sample sufficiency checks are complete.
