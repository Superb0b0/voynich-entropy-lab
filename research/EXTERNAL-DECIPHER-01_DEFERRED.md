# EXTERNAL-DECIPHER-01 — deferral and incident record

Date: 2026-11-26
Status: `DEFERRED_PENDING_CAL01_AND_PROTOCOL`

## Scope and procedural deviation
A separate branch and push-triggered workflow were created and ran before specific authorization for execution of unaudited external software and before numerical success criteria were preregistered. The general instruction to explore external resources was not sufficient to change the established research priorities. The completed run is retained as exploratory evidence only; it is not a qualified calibration, a validation of Decipher, or evidence of any Voynich cipher or plaintext.

## Immutable references
- Branch: research/external-decipher-01
- Original workflow commit: 06dc502bc6a5a9fba2e2703512d3b1191741ca2e
- Original workflow blob: 89e3f0e0739b29095f077b03b8822af92ac92d39
- Upstream Decipher: matthewdgreen/decipher, commit 2dace19a0309e08e9ea8e6c40af81c26f29276a3
- Run: https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/45889185080
- Job: https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/45889185080/job/140147337477
- Trigger: push; attempt 1; completed, success; created 2026-11-26T20:11:21Z.
- Corrective manual-only trigger commit: 1bdc5e75c5fc0988c20fb2e1747ea3cfb45759c4

## Observed exploratory results (job logs)
| Fixture | Reported character recovery | Reported word recovery | Reported solver time |
|---|---:|---:|---:|
| english_borg_analog_001 | 99.2% | 65.7% | 8.5 s |
| zodiac340_known_replay | 96.2% | 0.0% | 40.3 s |

Both reported automated mode and USD 0.00 model API cost. Zodiac uses a known transform replay, not blind recovery. Metrics are tool-reported and were not independently recomputed. No retrospective thresholds or PASS/FAIL qualification are assigned. A successful CI status means the commands exited successfully, not that recovery met a scientific threshold.

## Security and reproducibility limits
The original workflow used permissions: {}, did not explicitly reference secrets, did not check out the project corpus, pinned and checked the upstream commit, and contained no push command. Logs show installation of Python and Rust dependencies (37 wheel and 50 crate download lines), not all dependency versions/hashes were frozen, and no unexpected downloads or external model API calls were identified in the available logs. This is not a security audit or proof that no unlogged network activity occurred. No GitHub Actions artifacts were retained (API count 0); detailed fixture outputs were not recovered. Logs may expire. No manuscript corpus or protected HOLDOUT was intentionally provided to the workflow.

## Binding stop and priorities
No further execution, rerun, dispatch, integration, or manuscript test under this line until explicitly authorized after the existing priorities: article, CAL-01 verdict, then VOY-STATE-01 under its single gate. This branch is not to be merged into main merely to enable manual dispatch. The workflow trigger is manual-only; the workflow is not an authorization to run.

Before any future run: audit external code/install scripts and dependency provenance; freeze dependency versions and hashes, inputs, seeds, scoring/normalization, numerical character/word recovery thresholds, comparison nulls, budget and stop rule in a committed, SHA-256-hashed protocol approved before observing fresh results. Preserve output artifacts and logs. Existing exposed fixtures cannot provide a new blinded confirmation. Use fresh positive controls including Naibbe where applicable, matched negative controls (shuffle and Timm–Schinner-type generators), identical budgets and predeclared multiplicity control. Any manuscript assessment requires separate authorization, frozen rules, independent evaluation folios outside the protected HOLDOUT, and evidence beyond linguistic plausibility. A positive control only calibrates the specified solver on that control. Neither a positive nor a negative result establishes the existence or absence of a Voynich plaintext.

No new numerical thresholds are adopted in this record; they must be fixed prospectively. No new experiments are authorized by this record.
