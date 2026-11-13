# QO-RIVAL-01 independent local execution — 2026-11-13

Classification: **EXPLORATORY_NOT_VALIDATED**. No holdout folios included in statistics. Input file SHA-256 verified: `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.

Independent implementation of the corrected conditional-rate statistic, run locally using Python, seed 20261113, 2,000 permutations per null. This is not an independently preregistered discovery: the qo phenomenon was already known, and the statistic was amended after initial protocol publication.

- Training paragraph groups parsed: 115.
- Observed consecutive P-line qo→qo: 28 / 272 = 0.10294117647058823.
- Within-paragraph shuffle mean conditional rate: 0.16412778682411375; 95% Monte Carlo quantile interval [0.125, 0.20503597122302158]; one-sided depletion p=0.0004997501249375312.
- Within-folio shuffle mean conditional rate: 0.16394538588417817; 95% interval [0.12681159420289856, 0.20363636363636364]; one-sided depletion p=0.0004997501249375312.
- Holm-adjusted p for each of two comparisons: 0.0009995002498750624.

Interpretation: exploratory training signal survives both simple shuffle rivals; neither is a realistic full generative rival. No claim about translation, meaning, or decipherment. Next: parser cross-check and generator-rival calibration with frozen thresholds, without opening holdout.

Reproduction script available as conversation attachment `qo_rival_independent.py`; this report does not claim that GitHub CI executed successfully.
