# Attempt 001: archival reproducibility blocker

Date: 2026-11-15. Status: **NON VERIFICATO / BLOCKED**, not REPRODUCED or VALIDATED.

The general GitHub Actions verifier (run 43735980414, commit ded8c510f48781ee0fe434c49255f60e2f0782c8) successfully passed the previously blocking one-page inventory discrepancy and then stopped at `attempts/001-paragraph-header-key` with: `missing attempt.yml; cannot infer execution contract`.

The committed `attempts/001-paragraph-header-key/results.json` exists and records configuration and results. Direct checks did not locate `attempts/001-paragraph-header-key/run.sh`, `protocol.md`, or `README.md` on the research branch. These observations do not prove the original execution code is absent elsewhere in history.

**Do not** synthesize an `attempt.yml` or `run.sh` from the numbers in `results.json`. Do not exclude 001 from the general verifier or relabel CI as green. The archive must retain its historical result and its unverified status.

Next actions: (1) recover original source and invocation from documented provenance, if available; (2) compare source hashes and required inputs against the archive; (3) implement a holdout-safe replay with the original declared seed, outputs, and tolerance, preserving original result; (4) run full CI; (5) if original code is unavailable, formally classify the attempt as **NON REPRODUCIBILE** and create a separate *new* experiment with a new ID, not a retroactive replay.

The ANCHOR-02 independent confirmation remains **LOCKED_PENDING_GATE**. The protected holdout must remain sealed until full CI, independent parser review, and prospective sample sufficiency checks are complete.


## Provenance recovered (2026-11-15, subsequent investigation)

The original code **is present in repository history** at commit `0e87d9758f288cdeac29513ee04245dcd8126592`, whose diff includes `attempts/001-paragraph-header-key/run.py`, its original protocol, results, and `.github/workflows/attempt-001.yml`. The historical workflow runs Python 3.12 with NumPy 2.3.5, reads `experiments/line-memory/experiment/inputs/ZL3b-n.txt` and the RC1.2 parser, and compares the complete JSON output. The historical script explicitly asserts the SHA256 of the **complete** original corpus and expects 4,130 records. See https://github.com/Superb0b0/voynich-entropy-lab/commit/0e87d9758f288cdeac29513ee04245dcd8126592 .

**Correction:** The original source is not missing. The remaining blocker is a **methodological incompatibility**: a full-corpus historical replay cannot be passed off as a train-only holdout-safe replay. Do not waive input isolation, weaken source SHA checks, alter historical results, or silently classify 001 as reproduced under the new gate.

Two honest paths must remain separate:
- **Historical archival verification:** compare the archived source, protocol, script hash and original workflow to the original results, without reading or running the full corpus in a way that breaches the protected holdout policy. This is a provenance check, not a new clean replay.
- **New compliant experiment:** create a new ID and preregister a filtered-corpus protocol, with new baseline and new results. It cannot certify attempt 001 retrospectively.

Status: `001 HISTORICAL SOURCE RECOVERED; REPLAY UNDER CURRENT HOLDOUT POLICY NOT YET DEMONSTRATED`. Full CI remains red; ANCHOR-02 independent holdout remains sealed.
