# Attempt 011 — CI verdict (2026-11-15)
Run 43735733869, job 132877827758: SUCCESS. Artifact results-ci-011 uploaded. Training-only IT2a SHA-256 a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c. Parameters frozen from ZL3b 005; no IT2a refitting.

Primary qoqo:
- fit0_pred1: observed 2; M1 interval [3,12] OUT; M2 [0,7] IN.
- fit1_pred0: observed 12; M1 interval [20,36] OUT; M2 [3,14] IN.
Preregistered endpoint: M2_DISCRIMINATES_M1 (PASS).

Secondary metrics:
- fit0_pred1 M2: same_nonqo 128 [97,131] IN; repeat 5 [1,9] IN; triple windows 21 [10,25] IN; lag2 204 [202,248] IN.
- fit0_pred1 M1: same_nonqo 128 [92,124] OUT; repeat 5 [1,9] IN; triple windows 21 [9,23] IN; lag2 204 [205,256] OUT.
- fit1_pred0 M2: same_nonqo 161 [155,199] IN; repeat 7 [2,10] IN; triple windows 20 [16,36] IN; lag2 358 [333,396] IN.
- fit1_pred0 M1: same_nonqo 161 [150,190] IN; repeat 7 [3,13] IN; triple windows 20 [16,37] IN; lag2 358 [331,387] IN.

**Limitations**: EXPLORATORY. IT2a and ZL3b transcribe the same Voynich manuscript, so not independent source material. M2 was motivated by observations from the same manuscript. Prediction intervals reflect simulation with frozen point estimates and do not propagate fit uncertainty; no convergence diagnosis or likelihood-based model selection. CI confirms execution only. Repository-wide verifier separately FAIL. No holdout opened. No claim of decipherment or causal identification.
