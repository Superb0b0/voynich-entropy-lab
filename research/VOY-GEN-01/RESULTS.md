# VOY-GEN-01 — exploratory results, 2026-11-26

## Results

Same historical CAL-01 estimator, existing development geometry, no new HOLDOUT access intended. Pilot run 45841149462, artifact 15127224934; real reference run 45841639410, artifact 15128816174. Values below transcribed from the previously reported artifact inspection; no fresh computation in this closure.

| Quantity | ZL3b | IT2a |
|---|---:|---:|
| Transitions | 2977 | 2936 |
| CAL-01 mean gain | 0.001057 | 0.000979 |
| CAL-01 H1 valid | 3/20 | 3/20 |
| Real gain | 0.012038 | 0.012139 |
| Real conditional 95% CI | [0.003283,0.020720] | [0.003896,0.020172] |
| Real H1 valid | yes | yes |
| A mean gain | 0.020931 | 0.020343 |
| A observed range | [0.013949,0.028785] | [0.014381,0.027913] |
| A H1 valid | 20/20 | 20/20 |

Gain in nat per transition. A uses P(q|q)=.10, P(q|other)=.30, paragraph reset, initial probability .25 and iid interior .25, arbitrary exploratory settings, not calibrated. Seeds 1–20 separately per geometry. A explicitly encodes the target dependency, so this is a positive control, not an explanatory model. CAL-01 and A differ in more than the level of description; causal attribution to that factor alone is not justified. The real conditional CI and synthetic observed range are different statistical objects; their overlap neither establishes compatibility nor rules out a difference. No formal comparison was performed. Both transcriptions represent one manuscript.

## Decision

EXPLORATORY COMPLETE. Do not tune A, implement B/C or run reflow here. Real H1 is detected in both historical transcription datasets. The next question is robustness to actual transcription disagreements, not arbitrary synthetic perturbation or a new generator. No new empirical computation performed in writing this closure. Prior CAL-01 closure remains unchanged.
