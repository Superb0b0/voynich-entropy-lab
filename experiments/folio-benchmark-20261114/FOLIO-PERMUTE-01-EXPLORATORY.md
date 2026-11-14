# FOLIO-PERMUTE-01 — exploratory falsification (2026-11-14)

Status: EXPLORATORY, NOT CI REPRODUCED, NOT SCIENTIFICALLY VALIDATED.

Question: does exact adjacent-word repetition exceed a null model preserving each held-out folio's exact word multiset?

Inputs: GitHub fetched data/ZL3b-n.txt and data/IT2a-n.txt, without independent full-file SHA256 recalculation in this execution. HOLDOUT.md protected folios excluded before parsing; protected IDs never logged. Simplified IVTFF P-line regex, lowercase [a-z]+ extraction, eligible folios >=30 words. Deterministic 20% test split after LCG seed 20261114. Each corpus has 30 test folios.

For each folio, Fisher-Yates shuffle all its extracted words, independently, preserving each folio's exact word frequencies and number of tokens; count exact equal adjacent words within each folio. 10,000 replicates with LCG seed 20261116. Expected count computed analytically as sum over folios of sum_w count(w)*(count(w)-1)/folio_length. One-sided Monte Carlo p = (number of simulations with repeats >= observed +1)/(10000+1). Quantiles are empirical order statistics. Folio boundaries respected; line boundaries NOT preserved.

| corpus | pairs | observed | analytical expected | simulation mean | 2.5% | 97.5% | p one-sided |
| ZL3b | 4706 | 38 | 32.47671918125543 | 32.3861 | 22 | 44 | 0.17748225177482252 |
| IT2a | 4156 | 38 | 35.83399871144678 | 35.935 | 25 | 48 | 0.38166183381661833 |

Verdict: no statistically persuasive excess of exact adjacent-word repeats under a folio-preserving permutation null. Prior WORD-MEMORY-01 IT2a ratio ~2.30 versus pooled training lexicon is largely explained by folio-specific lexical composition. Does not rule out other forms of word-to-word dependence. Limitations: simplistic parser, line boundaries not preserved, single held-out split, no CI reproduction, no external calibration. No change to frozen RC1.4.2/V7.1.
