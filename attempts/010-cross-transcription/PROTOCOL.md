# Attempt 010: fixed M2 cross-transcription falsification
Preregistered before run; HOLDOUT CLOSED. This is a robustness test on a second transcription of the SAME manuscript, not independent source text.

Input: training-only filtered IT2a-n.txt, SHA-256 a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c. Fail closed on mismatch. Same parser and folio split as 005/006. Parameters FROZEN from ZL3b attempt 005 results.json: fit0_pred1 theta=0.815843 phi=1.091503; fit1_pred0 theta=0.694776 phi=1.675. No refitting on IT2a.

Primary: three statistics from 005 (same_nonqo, qoqo, repeat) and two from 009 (overlapping same-class length-three windows, lag2 same-class), 200 MCMC simulations, 95% intervals index 5 and 194, seed 20261121+100*fit+pred. PASS only if all ten cells fall within intervals. Otherwise FAIL, report each cell. This is distinct from 006 (which refitted on IT2a).

009's run3 counts overlapping triple windows, NOT maximal runs; preserve implemented definition and label correctly. Both valid consecutive pairs are required for each window. No holdout, no tuning, no merge.
