# Attempt 013 — verdict and audit (2026-11-15)

Run 43736738389, job 132880898606: SUCCESS. Python 3.11.18. Trusted preparation completed for ZL3b and IT2a training-only corpora; strace audit ended "strace input isolation PASS". The separate repository-wide "Verify archived attempts" workflow in the same commit failed; do not describe the repository CI as green.

## Primary endpoint
Observed qoqo: fit0_pred1=2; fit1_pred0=12.
- M2 intervals: [0,6] and [3,14], both cover.
- S1 intervals: [2,11] and [19,37], only first covers.
Preregistered verdict: M2_WINS_QO_ENDPOINT. This is limited to the preregistered primary statistic and these splits.

## Fitted S1 parameters
- fit0_pred1: theta=1.00, lambda=0.00; training loss=5.332837.
- fit1_pred0: theta=0.75, lambda=0.00; training loss=0.780097.
The qo-specific distance-2 parameter reached the lower grid boundary in both fits. This is not evidence that the data prefer a zero effect with precision; it is a boundary estimate on the chosen coarse grid and objective. S1's design did not reproduce M2's qoqo suppression in fit1_pred0.

## Secondary failures (must remain visible)
M2:
- fit0_pred1 lag2_sameclass observed 204, interval [205,249]: OUT.
- fit1_pred0 qo_distance2 observed 72, interval [50,71]: OUT.
S1:
- fit0_pred1 same_all observed 130, interval [91,121]: OUT; lag2_sameclass 204 [207,254]: OUT.
- fit1_pred0 same_all 173 [175,224]: OUT; qoqo 12 [19,37]: OUT; qo_distance2 72 [41,62]: OUT.
Therefore neither model passes all secondary checks. Do not summarize as a general 10/10 or total model victory.

## Methodological caveats
1. The primary endpoint is a predictive-interval coverage rule, not a calibrated model-comparison test, Bayes factor, likelihood ratio, or estimate of posterior model probability.
2. Only 200 predictive replicates and fixed point parameter estimates; parameter-estimation uncertainty and MCMC convergence/effective sample size are not quantified.
3. The S1 objective fits same_all and qo_distance2 on ZL3b, whereas M2's parameters originate in attempt 005 fitting same_nonqo and qoqo. Equal parameter count does not make the fitting objectives or target features identical. This is a legitimate alternative hypothesis comparison, but not a fully symmetric equal-objective competition.
4. ZL3b and IT2a are transcriptions of the same manuscript, not independent manuscripts.
5. strace audit PASS applies to attempt process file opens in this workflow; repository-wide verifier failure remains separate.

Status: EXPLORATORY RESULT. M2 wins the predeclared qoqo endpoint against this S1 implementation; mechanism not identified, no decipherment claim.
