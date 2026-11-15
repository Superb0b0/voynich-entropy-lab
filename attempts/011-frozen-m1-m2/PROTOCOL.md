# Attempt 011: frozen M2 versus frozen M1 on IT2a
Preregistered before any 011 measurement. Holdout CLOSED. Uses same training-only IT2a, hash a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c.

**Models**: M2 theta/phi and M1 theta_all/phi=0 from 005's ZL3b fits. Both frozen. Same IT2a groups, seed 20261121+100*fit+pred, 200 predictive draws per model and direction, exact MCMC implementation from 010.

**Primary discriminatory statistic**: qoqo. M2 wins only if in BOTH directions qoqo observed lies inside M2 95% interval and OUTSIDE M1 95% interval. Otherwise not supported. **Secondary**: other four 010 metrics for both models, reported with no extra success threshold. This is an exploratory, training-only, cross-transcription comparison; M2 was introduced after studying the same manuscript and is not independently confirmed. Do not compare with TS under mismatched segmentation.

CI status does not equal scientific validation. Never open holdout, refit, or tune after seeing results.
