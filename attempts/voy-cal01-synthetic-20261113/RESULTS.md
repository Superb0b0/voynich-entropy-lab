# CAL-01 synthetic calibration checkpoint (2026-11-13)

Status: SYNTHETIC_CALIBRATION_ONLY; **not** a qualifying scientific attempt and **not** independent Voynich validation.

Pre-run parameters: seed 20261113; 400 calibration IID replicates; 400 independent evaluation replicates per generator; 120 groups of 8 observations; alpha=0.01. IID Bernoulli(0.35) versus anti-persistent binary Markov generator with P(1|1)=0.08 and P(1|0)=0.50. Statistic P(1|1)-P(1|0); reject IID below the lower 1% empirical IID calibration quantile. Predefined PASS: FPR <=0.025 and power >=0.80.

Executed locally with Python standard library. Threshold -0.08125490966221521; independent IID evaluation 3/400 flagged (FPR 0.0075); anti-persistent evaluation 400/400 flagged (power 1.0). PASS for these synthetic generators only.

Local executed script SHA-256: `cf192d482fd320c96cb22912ce131df3e1751fa667cf4435c014c3e6a50b496e`; local JSON results SHA-256: `2fb6dc9cf68c227687c6e577472bde3b5941860fa00bf7f4bf32bc2bd4acd8e9`. Executed script and JSON supplied separately as downloadable conversation artifacts; this GitHub commit archives the report only, **not** the full reproducibility bundle. Do not mark REPRODUCED or VALIDATED.

No Voynich corpus, holdout folios, frozen anchors or RC1.4.2 artifacts accessed or changed. Limitations: not yet tested against ms408/Naibbe/Timm-Schinner; no transcript comparison, folio split or confound controls. Next: upload executable bundle and validate external rival generator inputs before any qualifying experiment. The historical public holdout is compromised; see issue #4.