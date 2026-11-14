# 006 verdict — 2026-11-14

**EXPLORATORY SIGNAL, NOT SCIENTIFICALLY VALIDATED.**

The preregistration was committed before the first execution of attempt 006. Training-only input SHA-256: `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9`. Local execution: 1000 simulations per rival and folio split; seed 20261118.

Split 0: 12 observed qo→qo transitions among 263 qo predecessors; within-paragraph shuffle mean 49.011 (p=0.000999), character-Markov mean 33.999 (p=0.000999).
Split 1: 2 observed among 133 qo predecessors; shuffle mean 15.371 (p=0.000999), character-Markov mean 13.319 (p=0.001998).
Holm-adjusted p for all four comparisons: 0.003996 each. Prespecified exploratory numerical thresholds met.

**Critical limits:** This is a known signal from attempt 004; no independent holdout was opened. The character-Markov rival is an internal model, not an independent reproduction of external generator packages. It does not preserve all lexical, positional, Currier, scribal and layout dependencies. Both null models may be inadequate. No translation or decipherment claim.

**CI status:** PENDING until a green run for the results commit is inspected. A green CI establishes replay consistency and input isolation only, not scientific validity.
