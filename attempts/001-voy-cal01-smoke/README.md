# 001 — Synthetic mechanism smoke test
Date: 2026-11-13. Status: EXPLORATORY / INCONCLUSIVE FOR VOYNICH.
Hypothesis: lag-1 same-symbol fraction discriminates trivial alternating vs IID binary generator at n=200.
Predeclared smoke criterion: alternating <= 0.10 and IID within [0.35, 0.65]. Seed 20261113. Runtime budget < 10 s. Data generated locally; no Voynich files used. Negative control IID.
Observed: alternating 0/199 = 0; IID 98/199 = 0.49246231155778897. Criterion passed. No p-value or CI inferential claim. Obvious alternative: alternating mechanism is trivial and calibration not representative of Voynich. Verdict: synthetic smoke PASS; scientific mechanism identification INCONCLUSIVE. Next: calibrate against realistic rival generators.
Script SHA-256: 6b816419e7b8fd04813e68ac65bd7f36fbb253532492918545dcccbcc4b3ade8.
