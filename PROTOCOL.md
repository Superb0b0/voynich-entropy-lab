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
