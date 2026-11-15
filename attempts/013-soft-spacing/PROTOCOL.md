# Attempt 013 — fair probabilistic competitor (preregistered)
Status: DESIGN_LOCKED; NOT RUN; NO RESULT. Holdout CLOSED.

## Hypotheses
M2: original 005 two-parameter local refractory model. Rival S1: **probabilistic soft-spacing** model with two free parameters, a generic same-class adjacency penalty theta and a qo-specific distance-2 spacing penalty lambda. Unlike M2, S1 does not assign an additional cost to qo->qo adjacency; its qo-specific penalty acts on pairs of qo first words at exactly two consecutive valid links apart. Energy E=theta*(number of valid same-class adjacent pairs) + lambda*(number of qo pairs separated by exactly one intervening first word and two valid links). This tests a distinct, non-identical finite-range mechanism. Same exact paragraph word multiset and validity mask as M2.

## Equal fitting budget
Fit theta and lambda **only on the ZL3b training split** in each direction using preregistered fixed grid theta in {0,0.25,...,2.5} and lambda in {0,0.25,...,3.0}, minimizing standardized squared discrepancies of two predeclared ZL3b sufficient features: all same-class adjacent count and qo distance-2 count. Tie-break: smaller theta, then smaller lambda. Grid fitting must use deterministic Monte Carlo with >=200 independent predictive replicates per grid point; if computation exceeds budget, stop and report INCOMPLETE, do not reduce grid after seeing IT2a. M2 parameters are frozen from 005 and may not be refitted.

## Test
Freeze S1 parameter estimates and evaluate both models on IT2a training-only folios in both prediction directions, using 200 replicates per direction and same exact preprocessing SHA a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c. Primary endpoint: qoqo predictive coverage in both directions. Secondary: same_nonqo, exact repeat, triple windows and lag2_sameclass, plus the qo-distance-2 statistic. Report full observed counts and 95% intervals for both, including all failures. If both cover qoqo, uniqueness NOT established; if only M2 covers both, M2 wins this endpoint; otherwise INCONCLUSIVE.

## Scientific/operational gates
Before running, independent code review must verify 012's sampler and the fitted competitor, correct validity masks, reproducible seeds, no parameter tuning on IT2a, and proper data isolation. The trusted preparation tool must run before the audited attempt; use strace to block direct reads of original data and HOLDOUT.md. CI green alone never means VALIDATED. The ZL3b/IT2a transcriptions are not independent manuscripts; both are of Voynich. No holdout use. Do not interpret a fit as decipherment.
