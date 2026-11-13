# CAL-01 STRESS-05 (2026-11-13)

Status: **EXPLORATORY_STRESS_TEST**, not REPRODUCED or VALIDATED; no Voynich text or holdout accessed.

Independent local Python execution: 400 simulations per family, 120 groups of 8 observations, seed 20261113, threshold -0.08125490966221521 calibrated on iid Bernoulli(.35). Statistic P(1|1)-P(1|0), lower-tail rejection.

| Generator | Rejections / 400 | Mean statistic |
|---|---:|---:|
| iid | 3 | 0.000188 |
| heterogeneous groups p=.08/.62 | 0 | 0.318731 |
| beta-mixture groups beta(1.4,2.6) | 0 | 0.196004 |
| within-group drift p=.12 to .58 | 0 | 0.129349 |
| anti-persistent Markov p(1|1)=.08, p(1|0)=.50 | 400 | -0.420553 |
| persistent Markov p(1|1)=.65, p(1|0)=.19 | 0 | 0.454502 |

Interpretation: these synthetic controls did not cause a spurious lower-tail signal; positive control recovered. **Not** proof of general robustness, a manuscript-level signal, or decipherment. This statistic is explicitly one-sided, and cannot detect persistence by design. Further work: stronger adversarial nulls, other rival generators, folio-aware controls, multiplicity, transcription differences, then private independent confirmation.

Executed local script SHA-256: `dbc8f883fbc479e06d50da2fe583e223dff158ed92b5a35312c9ad6f5b44609a`. Results JSON SHA-256: `b1317a164289a838714d73e702c875c51eabc52e9a186e3911619cbd3ee85b54`. Files delivered as conversation artifacts; report-only commit, do not mark reproducible in CI.

Original protected anchors, RC1.4.2 and historical holdout untouched.