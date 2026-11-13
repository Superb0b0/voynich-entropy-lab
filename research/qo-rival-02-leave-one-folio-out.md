# QO-RIVAL-02 — leave-one-folio-out robustness (exploratory, post-hoc)

Date: 2026-11-13. Corpus ZL3b-n SHA256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`, verified locally.

Reuses the parser and train-only exclusions from QO-RIVAL-01. 115 training paragraph groups, 1,988 adjacent P-line pairs, 59 training leaves with qo eligible pairs.

Observed qo→qo 28/272 = **10.2941%**. Within-paragraph first-word shuffle (2,000 replicates, seed 20261113) mean conditional rate **16.4128%**, one-sided Monte Carlo p=**0.00049975** (uncorrected; this is a follow-up analysis, not independent confirmatory evidence).

Leave-one-folio-out sensitivity: for each of 59 leaves contributing qo pairs, remove its observed counts, compare observed conditional rate with the approximate null rate obtained from the other leaves' mean shuffled counts. **59/59** removals retain the depletion direction. Observed LOO rates range **9.09%–10.81%**.

Caveats: post-hoc analysis; approximate null rate in LOO is ratio of expected numerator and denominator, not permutation p-values for each deletion. No multiple-testing claim for the 59 leave-one-out comparisons. Folio clustering, parser agreement, and stronger generative rivals remain unverified. Holdout leaves excluded from metrics; raw source read for checksum. Scientific status: **EXPLORATORY_NOT_VALIDATED**.

Reproducible local script and JSON were generated in this ChatGPT execution; no assertion that GitHub Actions has executed the new test.
