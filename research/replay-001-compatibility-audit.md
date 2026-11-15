# Replay compatibility audit for historical attempt 001

Status: **NOT REPRODUCIBLE UNDER TRAIN_ONLY**. No protected folio was read by this audit; only source code, manifest and historical aggregate results were inspected.

Evidence:
- `attempts/001-paragraph-header-key/attempt.yml` is absent. The existing verifier stops here, as confirmed by Actions run 43722326048.
- `run.py` requires the **full-corpus SHA-256** `bf5b6d4a…beccafc` and asserts exactly **4,130** P records. Both are incompatible with a legitimately filtered training corpus.
- The historical result `results.json` reports **158 eligible folios** and 16,309 body tokens, so it cannot be relabeled as a training-only replay.
- The script's `--parser` and `--corpus` arguments require explicit paths. No safe `VOYNICH_DATA_DIR` adapter exists for this attempt.

Decision:
1. Do **not** fabricate `attempt.yml`, alter the archived `results.json`, disable the checksum, or mark attempt 001 as reproduced.
2. Keep historical 001 as **EXPLORATORY / NON VERIFICATO**.
3. For any new experiment, preregister a separate training-only attempt with its own hash, sample counts, rival and replay; never compare its outputs against historical 001 as if identical.
4. The separate private-training preflight CI success does **not** authorize a scientific result.

CI evidence: PR #12 private preflight run 43722325971 SUCCESS; archived attempt verifier run 43722326048 FAILURE.
