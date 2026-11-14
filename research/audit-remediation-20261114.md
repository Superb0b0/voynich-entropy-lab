# Independent audit remediation plan — 2026-11-14

Status: **BLOCKED / NON VERIFICATO**. This document does not certify any scientific result.
Scope: attempts 001–004 on `main`, read-only audit of original evidence.
The original `results.json`, protocols, and frozen materials must remain unchanged.

## Confirmed blockers

1. `.github/workflows/verify.yml` is red on run 43575127056. The job log says:
   `001-paragraph-header-key: missing attempt.yml; cannot infer execution contract`.
2. No archived attempt has `attempt.yml`. None has the required `run.sh`.
3. Attempts 001 and 002 demand the **full corpus hash** and, for 001, exactly **4,130 P records**. A holdout-filtered corpus cannot pass those invariants unchanged. Both historic runs therefore cannot be replayed under the current protected-input gate simply by adding a YAML file.
4. Attempt 004 opens `data/ZL3b-n.txt` directly and hardcodes the protected folio set. Its current stdout JSON schema differs from its archived `results.json`; a direct bytewise/schema comparison cannot pass. Attempt 003 relies on the same shared calculation rather than a standalone runner.
5. The existing verifier blocks direct opens of original `data/*.txt`, but a scientific holdout guarantee also requires preventing reconstruction through other corpus copies, scripts, or precomputed aggregates. A green replay check alone is not independent scientific validation.
6. Attempts 001–004 are exploratory historical evidence. They must remain NON VERIFICATO for the current `verify.yml` gate until an applicable green run exists. Previous individual green reproducibility jobs for 001/002 do **not** override this status.

## Safe sequence (no rewriting of history)

1. **Preserve originals.** Freeze the current 001–004 directory contents and hashes. Do not silently rewrite the old `results.json` to fit a new verifier.
2. **Split validation tracks.** Add a separately named `historical-replay` track that verifies original inputs/results while explicitly marking any historic holdout exposure; do **not** call this a qualifying current-protocol attempt. Keep `verify.yml` strict for new protected-data attempts.
3. **New qualifying attempts, new IDs.** Implement a separate training-only runner that accepts `VOYNICH_DATA_DIR`, reads no original corpus or holdout listing, uses an input-specific training hash, and emits `results_ci.json` in the exact archived schema. Add `attempt.yml` and an immutable preregistration before observing outputs. Do not reuse 001–004 IDs to disguise changes in method or data.
4. **Scientific controls.** Include at least one independently implemented rival generator (e.g. ms408, Naibbe, Timm–Schinner), folio-level partitioning, parser/layout/hand/line-length checks, family-wide Holm or FDR, explicit decision threshold, seeds, budgets and negative-control calibration.
5. **Test isolation.** Verify by instrumented file-open tracing that no original corpus, HOLDOUT.md or alternate full-corpus copies are accessed. Ensure the training-only input itself has a recorded SHA-256 and excludes all protected folios/pages. A failed isolation check means stop, not an automatic downgrade of protections.
6. **Require green CI.** Run the dedicated verification workflow, inspect logs and generated artifacts, then update TESTS.md with links and precise status. Green means reproducible under the verifier, **not** validated or deciphered.
7. **Independent holdout.** Do not open the protected holdout without a separate, explicit user-approved release plan. Independent holdout confirmation remains pending.

## Evidence and status

- Run 43575127056: **FAILURE**, missing `attempt.yml` at 001.
- Runs 43475878886 and 43476801393: historical 001/002 reproduction **SUCCESS**; different, weaker verification target.
- `TESTS.md`: 001–004 are **NON VERIFICATO** under the mandatory current CI gate.
- No new scientific outcome or p-value is claimed by this plan.

## Immediate engineering task

Implement the two-track verification design and regression tests on this branch. Do not relax the current holdout rule, reclassify historical experiments, overwrite evidence, or merge until both the new training-only verifier and the explicitly labeled historical replay are separately green.
