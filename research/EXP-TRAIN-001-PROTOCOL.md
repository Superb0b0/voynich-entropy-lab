# EXP-TRAIN-001: adjacency of lexical prefixes, training-only

Status: PREREGISTERED / NOT EXECUTED. Frozen before any experiment execution.

## Scope and protection
Only ZL3b-n.txt with *entire protected pages removed*, using HOLDOUT.md **inside the CI process only**. Never output protected IDs, full training text, page lists, or per-page metrics. Training is temporary and deleted at job end. No validation on holdout; no use of xenoglyph-ai/voynich-public V7.1 profiles. No builder, PCA, clustering or conditional coupling.

## Hypothesis and null
H1: adjacent eligible P lines within a page share more 3-character EVA token prefixes than a within-page random reordering of those lines.
Primary statistic: mean of per-adjacent-pair Jaccard similarities of sets of 3-character prefixes, pooled across all eligible within-page adjacent P-line pairs. An eligible line has >=2 alphabetic tokens of length >=3. Empty-union pairs are excluded. Only pages with >=3 eligible P lines enter the test.

Null: independently permute eligible line order within each eligible page, retaining line content and number of lines, using Python random.Random(20261115), 999 permutations. Statistic recomputed on permuted adjacent pairs. One-sided p=(1 + #null >= observed)/1000. Report observed, null mean, observed-minus-null, p, number of eligible pages and pairs. Threshold p<=0.01 is *exploratory support only*; otherwise not supported. No feature or threshold tuning.

## Parser contract
IVTFF page headers match `^<(f[0-9]+[rv][0-9]*)>\\s+<!`; P lines are only lines with a locus marker containing `,P` or `;P` (parser must document exact matching before execution). Extract EVA words only from the text following the closing locus tag; strip editorial marks and use ASCII [a-z] sequences. Fail closed if the parser cannot identify page blocks, eligible lines or valid tokens. Training-only SHA-256 must be checked internally but not published. Verify all protected pages absent from temporary corpus.

## Interpretation
Even p<=0.01 establishes only nonrandom adjacency under this particular null. It does not decipher Voynich, identify meanings or prove any historical mechanism. No comparison with historical 001 as a replay. Independent implementation and CI replay are prerequisites to REPRODUCED; scientific validation remains a separate gate.

## Locked inputs
Source ZL3b-n.txt SHA-256: bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc.
Holdout: repository HOLDOUT.md, private within runner. Seed 20261115; 999 permutations. All test choices above fixed before execution.
