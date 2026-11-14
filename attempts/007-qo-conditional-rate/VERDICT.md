# 007 verdict: conditional qo transition rate

**EXPLORATORY THRESHOLD MET, NOT SCIENTIFICALLY VALIDATED.**

Preregistration committed before local execution; fixed seed 20261119; input is the training-only sanitized corpus with SHA-256 `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9`.

| Folio split | Observed qo→qo / eligible qo | Observed rate | Shuffle null rate | Fixed-predecessor character Markov null rate |
|---|---:|---:|---:|---:|
| 0 | 12 / 263 | 0.04563 | 0.18851 | 0.13245 |
| 1 | 2 / 133 | 0.01504 | 0.11792 | 0.10092 |

All four one-sided Monte Carlo p=0.000999, all Holm-adjusted p=0.003996. All observed/null rate ratios <0.5. No zero-denominator draws. This corrects the **specific raw-hit denominator error** identified in 006.

**Limits:** qo was selected from earlier analysis, so this is not independent discovery; the character Markov null is internal, first-order, and does not reproduce external rivals (ms408, Naibbe, Timm–Schinner), folio-level dependencies, scribal/Currier factors or overlapping-pair dependence. A fixed predecessor null can break dependencies between adjacent generated successors. These comparisons do not establish translation, cryptography, or scientific validation. The protected holdout remains untouched. Independent external model replications and separately approved holdout validation remain pending.

CI replay status must be checked against the committed results; no promotion to VALIDATED on a green workflow.
