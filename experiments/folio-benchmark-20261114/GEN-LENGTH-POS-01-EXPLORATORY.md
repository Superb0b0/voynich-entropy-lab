# GEN-LENGTH-POS-01 (2026-11-14) — exploratory

Status: EXPLORATORY, NOT CI REPRODUCED, NOT VALIDATED.

Question: can a position- and length-conditioned character generator match held-out Voynich word statistics better than an unconstrained trigram generator?

Input: GitHub-fetched data/ZL3b-n.txt and data/IT2a-n.txt; original full SHA-256 not independently recomputed in this run. HOLDOUT.md protected folios excluded before data parsing, IDs never logged. Simplified IVTFF P-line regex and [a-z]+ word extraction, folios >=30 words. Split by sorted folio IDs shuffled with LCG seed 20261114, 20% test. ZL3b 124 train/30 test; IT2a 123 train/30 test.

Generator: for each test word length L, generate exactly L letters. At each character index i, sample from training empirical next-letter frequencies conditioned on (L,i,preceding two generated letters); fallback to training-wide preceding-two-letter frequencies, then literal 'o'. No test word letters used in generation. PRNG LCG seed 20261115. This generator has *oracle access to the held-out word length*, a significant advantage; cannot be treated as an unconditional generative account of word lengths. This test evaluates summary-statistic matching, not likelihood.

| corpus | words | metric | held-out real | length-position generator |
| ZL3b | 4736 | type/token | 0.33994932432432434 | 0.31271114864864863 |
| ZL3b | 4736 | adjacent repeat | 0.008025343189017951 | 0.008870116156283 |
| ZL3b | 4736 | suffix-2 entropy nats | 3.071150260545601 | 3.0099019990783344 |
| IT2a | 4186 | type/token | 0.34233158146201625 | 0.3559483994266603 |
| IT2a | 4186 | adjacent repeat | 0.00908004778972521 | 0.0033452807646356035 |
| IT2a | 4186 | suffix-2 entropy nats | 2.7178841532006044 | 2.7711494226082474 |

Verdict: several previously observed differences shrink strongly under positional and word-length constraints, especially suffix entropy and vocabulary variety. IT2a adjacent repetitions remain substantially undergenerated. No multi-seed uncertainty, calibration against natural-language/cipher controls, canonical parser, heldout log-loss, or CI. Cannot infer manuscript authorship, meaning, decipherment, or unique generator. No changes to frozen RC1.4.2/V7.1.
