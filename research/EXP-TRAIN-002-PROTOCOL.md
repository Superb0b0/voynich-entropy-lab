# EXP-TRAIN-002: within-paragraph adjacency control
Status: PREREGISTERED; must be committed before code execution.

Question: Does EXP-TRAIN-001 prefix-3 adjacency survive preserving paragraph boundaries?

Input and filtering: same source SHA-256, frozen RC1.2 parser, and protected-page exclusion as EXP-TRAIN-001. No holdout IDs or text in logs.

Paragraph boundaries: for each folio in physical P-record order, start a new paragraph at its first P record or when the corresponding source physical line contains the literal marker `<%>`. This matches the historic 001 paragraph segmentation convention. Do not merge across folios. Eligible lines: >=2 ASCII alphabetic tokens length >=3; prefix set of length 3. Retain paragraphs with >=3 eligible lines. Pairs: consecutive eligible lines *within* retained paragraphs only. Note: this is a different population/statistic from EXP-TRAIN-001, so compare significance rather than raw magnitudes.

Statistic: pooled mean pairwise Jaccard similarity of 3-character prefix sets on consecutive eligible lines. Null: shuffle eligible lines independently within each paragraph, preserving each paragraph's vocabulary, line count, and folio, 999 times, Python random.Random(20261116). One-sided p=(1 + count(null >= observed))/1000. Report aggregate paragraph count, pair count, observed, null mean, difference, p. p<=0.01 and positive difference = survives paragraph-preserving control, exploratory only. Otherwise not supported under this control; do not tune or repeat. No semantic inference.

No builder/PCA/clustering/coupling, no protected data published, no historical attempt modifications. This protocol must precede the first run.
