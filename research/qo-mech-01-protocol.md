# QO-MECH-01 — Frozen predictive mechanism test (training only)

Status: PREREGISTERED, NOT YET RUN at this commit. This is a **new predictive test**, not independent validation of the Voynich text.

Question: Is the depletion of first-word qo→qo better predicted by a binary first-order transition model than by an independent first-word qo-frequency model, on unseen training folios?

Input: only the isolated training snapshot produced by the QO isolated workflow, whose provenance is the locked full-corpus SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc. Neither HOLDOUT.md nor original corpus is present in the analysis job.

Parser and adjacency: reuse tools/qo_rival_calibration.py parse() and contiguous P-line pair selection, same page-paragraph boundaries. Binary state: first word starts with 'qo' (1), otherwise 0. Do not inspect semantic content.

Split: leaf IDs, deterministic SHA256("QO-MECH-01:"+leaf) parity into A/B. Train A/test B and train B/test A; all pairs from a leaf stay in one split.

Rival models: IID Bernoulli predicts P(next qo) from training second-token frequency; first-order binary Markov predicts P(next qo | current qo/nonqo) from training transition counts. Both use Laplace(1,1) smoothing, fixed before execution. Evaluate predictive log loss in nats per adjacent pair, on the *same* held-out training-leaf pairs.

Primary statistic: delta = mean_log_loss(IID) - mean_log_loss(Markov), separately for A→B and B→A. Positive delta favors Markov.

Death criterion: Markov mechanism supported provisionally ONLY if delta >= 0.005 nats/pair in BOTH directions. Otherwise mechanism NOT SUPPORTED. Require at least 30 qo predecessor pairs in each evaluation set and nonempty transitions in both training sets; otherwise INCONCLUSIVE. No post-hoc threshold change. This threshold is a predictive effect-size criterion, not a significance test.

Secondary diagnostic: observed qo→qo count/rate and Markov/IID predicted qo→qo counts on each evaluation split, using each evaluated pair's predecessor. No statistical significance claims without separate calibrated uncertainty analysis.

Reproducibility: run twice and require identical JSON bytes, fixed hash and protected-input guards. Never call this a decipherment or a validated rule of the Voynich. Preserve RC1.4.2 CLOSED_PENDING_VALIDATION.
