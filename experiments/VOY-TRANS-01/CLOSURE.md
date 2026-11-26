# VOY-TRANS-01 — Closure, 2026-11-26

**VOY_TRANS_01_COMPLETED — SIGNAL_PRESERVED_ON_ALIGNED_SUBSET — DISCORDANT_SUBSET_UNDERPOWERED — PARAGRAPH_STRUCTURE_DIVERGENCE_NOTED**

## Result
The original CAL-01 checkpoint (SHA-256 6043b1935029ba0e5b53e0cd9f65d0b70601b1d998e605840fa32cb805541a4d) was reopened and the frozen predictor functions replayed with NumPy 2.3.5 and scikit-learn 1.8.0, OPENBLAS_NUM_THREADS=1. Historical baseline gains reproduced exactly. The ordered locus pair is the key; transitions are adjacent within historical paragraphs of at least four lines, with nonempty endpoints. Concordance means agreement on both binary qo- opening indicators, not full lexical identity. Original folds, features, regularization and 10,000 leaf bootstrap draws retained.

| Sample | ZL3b n | ZL3b gain | IT2a n | IT2a gain |
|---|---:|---:|---:|---:|
| Full | 2977 | 0.012038152352543678 | 2936 | 0.012138546910961803 |
| Common | 2899 | 0.012899926345597718 | 2899 | 0.013036253507719659 |
| Concordant | 2881 | 0.012790995187192889 | 2881 | 0.01269908328156918 |
| Discordant | 18 | 0.030334963421392476 | 18 | 0.06700222137102725 |
| Noncommon | 78 | -0.01999111438929815 | 37 | -0.0581979780620389 |

These are evaluations of full-model out-of-fold predictions on each subset. Separate refits on the common sample yield 0.012928467478224102 and 0.012823661732108254; on concordant transitions 0.012661928147360235 and 0.012664481495578845 (relative difference approximately 0.02%). Discordant refits fail because a fold is empty; ZL3b noncommon refit fails because a training set contains one class. IT2a noncommon refit yields -0.015466804495711847. No fallback estimator used.

## Interpretation and limits
The signal persists on the physically aligned subset and does not require the 18 observed binary opening disagreements (0.62% of common transitions). The nearly identical concordant refits are descriptive convergence on the same manuscript, not independent replication. Discordant observations are too sparse for a meaningful test of general transcription sensitivity; no equivalence claim. On common pairs, paragraph position differs in 105 cases and paragraph length in 298; leaf, fold and Currier group agree throughout. Paragraph covariates were retained separately. This is not a demonstration of general transcription robustness, nor of a linguistic or cryptographic mechanism. The earlier label TRANSCRIPTION_ROBUST is withdrawn.

Stop here. No new thresholds, generators, paragraph analysis or HOLDOUT access. Historical code unchanged. This closure records the rerun numerical gains and limitations; it is not a complete archived replay bundle.
