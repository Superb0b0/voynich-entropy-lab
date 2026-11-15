# Attempt 014 — M2 parameter stability by paragraph bootstrap
Status: PREREGISTERED DESIGN; no results. HOLDOUT CLOSED.

## Question
Are the M2 parameters theta_nonqo and phi stable to resampling paragraphs within each ZL3b training split, or are the fitted values driven by a small number of paragraphs?

## Input and isolation
Use only trusted-prepared ZL3b training-only corpus, SHA-256 dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9. Trusted preparation occurs before attempt execution; attempt process receives only filtered file. strace must show no access to original corpus, HOLDOUT.md, or .git. Fail closed on hash mismatch.

## Bootstrap
Resample paragraph groups with replacement within each of the two fixed training partitions, preserving each sampled paragraph's words, classes, and validity mask. 500 bootstrap replicates per direction, fixed seed 20261115. Refit theta_nonqo and phi using the same parameter grids and fitting order as attempt 005, but with 200 predictive simulations per grid point for stable Monte Carlo. Report medians, 2.5/97.5 percentiles, boundary-hit frequencies, and convergence diagnostics for every chain (acceptance rate and split-chain R-hat where implementable).

## Predeclared interpretation
Parameter stability is supported only if (a) both 95% bootstrap intervals exclude zero for theta_nonqo and phi, (b) neither parameter hits a grid boundary in more than 5% of replicates, and (c) median absolute deviation / absolute median <= 0.5 for both parameters. Otherwise report instability or inconclusive, with no grid expansion after observing results.

## Secondary
For each bootstrap fit, report posterior-predictive qoqo coverage on the opposite ZL3b split using 200 draws. Do not tune based on coverage. Report distribution of coverage, not only pooled aggregate.

## Limits
This is internal stability on the same manuscript and training corpus, not independent validation. It cannot establish causal mechanism, language, decipherment, or uniqueness against all rivals. CI success is reproducibility only. No changes to 005, 013, holdout, baseline, or existing results.
