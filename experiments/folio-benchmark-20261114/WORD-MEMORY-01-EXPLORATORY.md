# WORD-MEMORY-01 — exploratory test (2026-11-14)

Status: EXPLORATORY, NOT CI REPRODUCED, NOT SCIENTIFICALLY VALIDATED.

Question: Is immediate exact-word repetition more frequent than predicted by a length-conditioned independent-word baseline?

Inputs: GitHub fetched data/ZL3b-n.txt and data/IT2a-n.txt (original SHA256 not recomputed here). Protected IDs from HOLDOUT.md excluded in memory before parsing, never printed. Simplified IVTFF P-line regex and [a-z]+ word extraction; eligible folios >=30 extracted words. Split 20% folios after deterministic LCG shuffle seed 20261114. ZL3b 124 training and 30 test folios; IT2a 123 training and 30 test folios.

For each adjacent pair (previous word a, current word b) within a test folio, compare exact repeat 1[a=b] to expected probability of sampling a from training-word empirical distribution conditioned on current word length len(b). Expected repeat count is sum of these probabilities over adjacent test pairs. This baseline uses test word lengths (oracle), and may fail to preserve folio-level lexical mixture, line boundaries, and adjacent-length dependence. No random sampling was required; expected counts computed analytically.

| corpus | adjacent pairs | observed exact repeats | expected repeats | observed/expected | test folios with observed > expected |
| ZL3b | 4706 | 38 | 30.060651152883313 | 1.2641110070017618 | 14/30 |
| IT2a | 4156 | 38 | 16.55119058928864 | 2.295907342435673 | 18/30 |

Interpretation: a pooled training lexicon independent-word baseline underpredicts exact repeats, more strongly for IT2a. This is not evidence of a specific causal memory mechanism: folio mixtures and local line structures are not controlled, and no significance interval or multiple-testing adjustment has been computed. Simplified parser may incorporate transcription markup. Next: preserve folio-specific vocabulary and line positions in a within-folio permutation control; compare across multiple seeds with uncertainty. No changes to frozen RC1.4.2/V7.1.
