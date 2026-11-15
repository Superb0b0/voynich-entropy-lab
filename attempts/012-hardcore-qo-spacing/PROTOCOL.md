# Attempt 012 — hard-core qo spacing challenger (preregistration)
Status: PREREGISTERED, no 012 results measured at protocol freeze. HOLDOUT CLOSED.

Question: can a structurally different mechanism reproduce the qo->qo suppression that favored M2 over M1 in attempt 011?

**H0 competitor S0 (hard-core qo spacing, no fitted parameter):** within each paragraph retain the exact multiset of first words, including all class counts. Uniformly shuffle non-qo words; place qo words uniformly in available slots to minimize the number of adjacent qo pairs over valid consecutive-line edges. Do not use theta/phi, M2 likelihood or learned transition weights. Sampling protocol: 200 independent random arrangements per paragraph and prediction split, with fixed Random seeds 20261121+100*fit+pred, deterministic tie handling. For small paragraphs use rejection or exhaustive minimum construction with deterministic algorithm; if uniformity cannot be established, explicitly label sampling approximate. Preserve paragraph boundaries, folio split and valid line-pair masks.

**M2 comparator:** frozen ZL3b parameters from 005, no refitting on IT2a, same predictive procedure as 011. Training-only IT2a hash a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c.

**Primary decision:** for each prediction direction, report observed qo->qo and empirical 95% interval for S0 and M2 (200 simulations). S0 challenges uniqueness if qo->qo observed is inside S0 intervals in BOTH directions. If S0 fails either direction while M2 passes both, M2 wins this specific endpoint. Otherwise report INCONCLUSIVE. No claim that any winning model is the real mechanism.

**Secondary:** same_nonqo, exact first-word repetition, overlapping same-class triple windows, lag2 class matching, same metrics as 011. Report without tuning or changing endpoint. Do not compare unrelated TS generator segmentation. Do not open holdout. CI success is not scientific validation.

**Mandatory methodological gate:** previous 009-011 scripts read full raw corpus and HOLDOUT.md inside the attempt before filtering; this is not acceptable as a verified isolation boundary. Before 012 may be marked REPRODUCED under strict verifier, move training-only corpus preparation to trusted CI/verifier and run attempt with access to filtered data only; audit file access. Until then all 012 results are EXPLORATORY regardless of CI green.
