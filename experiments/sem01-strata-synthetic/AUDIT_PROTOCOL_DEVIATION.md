# SEM01 synthetic reproducibility audit, 2026-11-14

**Outcome: NUMERIC REPRODUCTION PASS; PROTOCOL COMPLIANCE FAIL.**

Read the committed protocol and run.py from research/sem01-stratified-synthetic-20261114 and reran identical script locally with Python. Observed values: pooled_phi=0.530907, conditional_phi=0.063399, pooled_permutation_p=0.0005, stratified_permutation_p=0.565717, seed=20261114, B=2000. Protocol SHA256 d2374348eea24a01871b759019fdb1fd15e7b2d474248edfcfbff3940609c67b. Script SHA256 c74945e4e68bd06273de652dacbfc9828125ec9f044e42b9de32918fefe2f494.

**Deviation:** protocol explicitly specifies 40 folios per section and **10 observations per folio**. Actual code loops 40 times per section and appends exactly one (section,x,y) record per iteration: 80 total observations, not 800. No folio ID is stored. The shuffle therefore acts on 80 independent rows, not clustered observations within folios. Prior numerical claims are reproducible for this *different design* only. No retrospective rewrite of preregistration or reinterpretation as a folio-clustered experiment is allowed.

**Next action:** freeze a new protocol specifying folio identifiers, 10 observations per folio, within-folio dependence, and folio-block permutation; only then run a fresh calibration with a new ID. No Voynich data, private holdout, or frozen RC1.4.2/ANCHOR artifacts were accessed or modified.
