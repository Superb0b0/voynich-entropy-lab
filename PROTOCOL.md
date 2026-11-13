# PROTOCOL.md — Voynich autonomous research v1
Goal: decipher, translate, interpret and explain MS 408 and reconstruct its production, intended function, audience and mechanism. This protocol governs new work; repository evidence and frozen artifacts take precedence.

## Mandatory bootstrap
Read LOG.md, KNOWLEDGE.md, STATE.md, TESTS.md, HOLDOUT.md (only if user-selected), IDEAS.md, attempts/, experiments/line-memory/, src/pipeline.py and CI, on main and anchor-rev3-staging-20261112. Read xenoglyph-ai/voynich-public read-only. Verify full SHA-256 of ZL3b-n.txt and IT2a-n.txt before scientific use. Record missing files and discrepancies; never infer an absent file means a completed test. If no user-defined HOLDOUT.md exists, do not create one or expose holdout folios.

## Batch execution
Complete at least five qualifying attempts OR 60 minutes of work per batch, unless a genuine technical limit intervenes. After each commit, immediately proceed to the next cycle. A calibration/smoke test alone does not count as an attempt.
Each qualifying attempt requires (1) a falsifiable hypothesis on actual Voynich data, (2) a rival generator, (3) a folio-level split, (4) a TESTS.md entry. Before looking at outcomes, freeze numeric death criterion, budget, seed, complete data SHA-256, method and family. Calibrate novel methods on known generators within the attempt. Run code; test transcription, line length, hand, layout and parser confounds. Report numbers, intervals, exploratory/confirmed status and Holm/FDR multiplicity across the registered test family; unadjusted p-values are exploratory. Never promote a discovered result without independent holdout.

## Per-attempt archive
Append attempts/NNN-name/{protocol,code,inputs-manifest,results,verdict}, TESTS.md, LOG.md, KNOWLEDGE.md and STATE.md. Archive failures and inconclusive outcomes. Avoid duplicate hypotheses; reopening needs a new stated fact. Every third qualifying attempt explores outside the prior taxonomy. After five qualifying attempts, write lessons from failures; after ten, review recent literature and repositories and add dated sourced IDEAS.md entries. Commit on an authorized research branch without rewriting evidence or history. Do not mutate RC1.4.2 CLOSED_PENDING_VALIDATION, RP-01, f085v or frozen anchor staging.

## Priority
Known-generator calibration with ms408 DireLabs / pykeedy Naibbe / Timm–Schinner; folio-split qo- positional patterns and first-word avoidance; prespecified Currier/hand/quire heterogeneity; independent Takahashi replication; independent semantic anchors; medical Latin and iconographic comparisons. Explore substitution, nomenclators, transposition, artificial languages, mechanical generation, steganography, and alternative production functions without assuming any answer.

## Anti-stall and output
Never fabricate a result, citation, hash, run, or commit. If blocked by permissions, missing verified corpus, compute/time limit or missing user-defined holdout, record the exact blocker and next executable action in STATE.md; stop that run rather than mislabeling a smoke test as a scientific attempt. Never claim continuous execution outside scheduled runs. After a completed batch (or documented technical limit), report at most eight lines: qualifying attempt ID, hypothesis, verdict, commit, and next action.

## Mandatory CI verification gate (2026-11-13)
An archived attempt counts as a qualifying or verified attempt **only when the GitHub Actions `.github/workflows/verify.yml` job is green for the relevant commit**. A red, missing, skipped, or unconfirmed CI run means the result must be recorded as **NON VERIFICATO** in `TESTS.md`, regardless of local p-values or a successful commit. CI green establishes reproducibility under this verifier, **not** scientific validity or independent holdout confirmation.

For each `attempts/NNN-*/`, provide `attempt.yml` with an integer `seed`, a nonnegative numeric `tolerance`, and either `run.sh` or an explicit `command`; commit `results.json`. The replay must write `results_ci.json` in its attempt directory. The verifier checks SHA-256 for all `data/*.txt` against `MANIFEST.md`, replays every attempt, compares numeric fields within the declared absolute tolerance and other fields exactly, and fails closed on missing inputs or inaccessible holdout isolation.

`HOLDOUT.md` identifies protected folios/pages inside corpus files rather than a separate list of data files. To avoid leakage, the verifier supplies a filtered training-only corpus in `VOYNICH_DATA_DIR` and audits file opens with `strace`. Attempts that open original `data/*.txt` or `HOLDOUT.md` fail. Scripts must explicitly use the filtered directory and must not reconstruct held-out content from other inputs. If an attempt's input format cannot be safely filtered, verification fails rather than silently weakening protection.
