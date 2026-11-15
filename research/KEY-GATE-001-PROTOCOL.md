# KEY-GATE-001: preregistered decipherment falsifier

Status: DESIGN FROZEN; NOT EXECUTED; NO CANDIDATE KEY; NO DECIPHERMENT.
Date: 2026-11-15. Scope: experimental branch only. Never touch protected holdout until a valid key, evaluator, and control generator are frozen and audited.

## Eligibility
A candidate must supply a UTF-8 machine-readable mapping from explicit transcription units (with edition and segmentation specification) to output units; deterministic parsing and handling of nulls, abbreviations, ambiguities, and unknown symbols; an immutable SHA-256 of the full key, code, language reference corpus and evaluator; a dated provenance log identifying every manuscript locus consulted during key construction. Free interpretation, image-guided corrections, contextual exceptions, selective omission and retroactive expansion are forbidden. A key without all these is INELIGIBLE, not FAILED.

## Isolation
The existing HOLDOUT.md is confidential. Do not print or expose protected folio IDs or text. A separate training-only development partition, split by folio before candidate tuning, can be used for engineering and dry runs. Protected holdout is opened only once after registration and code audit. Every trial including an abandoned one is logged. No selection on protected results.

## Scoring (freeze exact algorithms before evaluation)
Score all contiguous decoded output, not handpicked words. Primary: normalized held-out per-character log likelihood under a *fixed*, external historical-language model trained only on authentic documents; report coverage and unknown-output fraction. Secondary: tokenization-free character cross entropy, grammatical agreement judged by blinded qualified readers using an immutable rubric, and blind semantic prediction of manuscript-independent anchors, where independently certified. A positive score alone is not a decipherment.

## Controls
For each candidate generate >=999 equally expressive rival keys with identical mapping cardinalities, null budget, output length and allowed expansions, and identical opportunity for fitting on the training portion. Include randomized bijections, frequency-constrained and bigram-constrained variants, and a matched-language reference; assess familywise error over all tried keys and languages. If constraints are infeasible, stop and declare the comparison non-comparable. Report all candidate and control scores, including failures.

## Precommitted decision
Reject a candidate if its score fails to exceed the 99.9th percentile of the matched null family, if coverage is below 95% of glyph units, if >1% output is silently dropped, or if any exception is introduced after freezing. With 999 rivals the minimum empirical one-sided p is 0.001; passing it is necessary but NOT sufficient. Require successful blind contiguous translation and independent reproduction before any claim of decipherment. If no eligible key is submitted, result is NOT EXECUTED, never PASS.

## Existing results
EXP-TRAIN-001/002 are adjacency tests, not tests of a decipherment key. Caspari–Faccini remains externally challenged; no independently verified deterministic mapping compatible with ZL3b transcription is registered. 'doaro = Toro' is unvalidated and cannot enter the candidate table as a fact.

## Execution gate
Before a run, commit: key.json, key.sha256, evaluator.py, language-model manifest, controls generator, complete dependency lock, expected output schema and signed preflight report. CI must verify immutability, isolation and controls. No historic attempt, main branch, or xenoglyph-ai/voynich-public modifications.
