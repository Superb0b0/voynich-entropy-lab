# 006 — preregistration: qo-to-qo first-word transition depletion (TRAIN ONLY)

Frozen before computing 006 outcomes on 2026-11-14. **EXPLORATORY**: qo signal and its direction were already discovered in 004; no independent confirmation is possible without separately authorized untouched holdout. Do not call this a new discovery.

Input: only `$VOYNICH_DATA_DIR/ZL3b-n.txt`, prefiltered by verifier. Required SHA-256 `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9`. No original data files, HOLDOUT.md, precomputed result tables or protected leaf IDs may be opened by runner.

Parser: page headers `<f...>`, P-locus lines, paragraphs split by `*P`/`@P`, first cleaned lowercase a-z token; adjacent numbered P rows within page/paragraph only. Folio split parity of SHA256(`str(leaf)+':20261114'`); both splits required. Exclude non-P lines and empty tokens.

Statistic per split: observed number of consecutive first-word qo-prefix pairs, conditional on predecessor beginning qo; denominator is number of eligible qo predecessors. Primary null: 1000 seeded within-paragraph first-word permutations preserving each paragraph's multiset and line adjacency. **Independent rival**: first-order character Markov generator trained exclusively on the training corpus's first words, with word-length distribution preserved, and independently generated first words at each eligible line; 1000 Monte Carlo simulations, same folio/paragraph/line geometry. Character generator is an *internal rival*, **not** a reproduction of DireLabs ms408, Naibbe or Timm–Schinner. Its limitations must be explicit.

Seed 20261118, permutations 1000 per rival per split. Family: 4 tests (two splits × two rivals); Holm correction across all four. Exploratory threshold for follow-up only: each split observed/null ratio <0.5 for each rival and all four Holm-adjusted one-sided p<=0.01. If any denominator zero or null mean zero: INCONCLUSIVE. No claim of independent validation regardless of significance.

Controls: report eligible folios, groups, qo predecessors, per-split observed/null, null 95% quantiles; do not interpret null-vs-real discrepancy as decipherment. Computational budget 600 s. Numeric output deterministic and compared exactly by CI. No holdout opened. Scientific verdict cannot be upgraded by green CI.
