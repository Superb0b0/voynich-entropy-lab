# COMPAT-014-01-A1 technical audit

This directory contains the aggregate-only comparison code and report for the preregistered M2 / RC1.2 compatibility audit. It is a technical parser comparison on the already-filtered ZL3b training input; it is not a scientific validation or an independent replication.

## Frozen inputs

- Training-only ZL3b input: SHA-256 `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9`, 323,741 bytes.
- Historical M2 parser source: `attempts/005-refractory-qo-parameter/run.py`, commit `c27a149313ed6d809ec30f9e384011b21b299c63`, SHA-256 `c522868b488707d8fe87e5a1d78683e29de28e9663c6eb1144d232f773e0118e`.
- Canonical parser: `ivtff_parser_rc1_2.py`, SHA-256 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`.

The audit runner accepts only the prepared file and verifies its digest before parsing. It does not read the original corpus or `HOLDOUT.md). The filtered file and per-locus diff are not included in this public branch. The per-locus table is retained separately; the public report contains aggregates only.

The report uses the COMPAT-014-01-A1 input hash above. A later W47 preflight snapshot has a different hash and is outside this audit.

## Run

From the repository root, provide the already-prepared file as `TRAINING_INPUT`:

```sh
python3 research/compat-014-01-a1/audit_compat014.py \
  --input "$TRAINING_INPUT" \
  --parser research/compat-014-01-a1/ivtff_parser_rc1_2.py \
  --m2-source attempts/005-refractory-qo-parameter/run.py \
  --private-diff /private/COMPAT_014_01_A1_locus_diff.csv \
  --out /private/COMPAT_014_01_A1_aggregate.json
```

## Compared definitions

- M2 full-token counts are collected using the historical 005 cleanup and tokenizer before its `tok[0]` selection. M2's historical paragraph unit is the per-page grouping made by `@P`/`*P`; its valid-pair mask follows the historical numeric-locus increment.
- RC1.2 token counts use the verified parser's `[A-Za-z]+` extraction. RC1.2 units are IVTFF `<%>` … `<$>` blocks reset at page boundaries. The strict adjacency mask requires both physical P-row contiguity and consecutive numeric locus indices, following the repository structural audit.
- Locus sets, full-token counts, first-token identity/class, unit co-membership, and valid arcs are reported separately, for total and Currier A/B splits. The 99% secondary thresholds are descriptive and cannot establish equivalence.

The audit is limited to the same manuscript and a training subset already exposed to prior analyses. No M2 fitting, bootstrap, holdout evaluation, or scientific validation is performed.
