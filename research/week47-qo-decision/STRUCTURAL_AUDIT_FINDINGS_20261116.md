# W47 structural audit: verified aggregate evidence (2026-11-16)

Source: GitHub Actions run [43866019325](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866019325), job structural-audit, artifact ID **14225062278**, file `w47-structural-audit.json`. This is a transcription-structure audit, **not** a scientific test or a parser-parity attestation. The artifact was inspected directly; no protected folio IDs or manuscript text are reproduced here.

| Measure | ZL3b | IT2a |
|---|---:|---:|
| Structural blocks | 740 | 772 |
| P loci | 4,130 | 4,118 |
| P loci inside blocks | 4,117 | 4,118 |
| P loci outside blocks | 13 | 0 |
| Strict physical adjacent pairs | 3,281 | 3,307 |
| Gap or out-of-order adjacent rows | 38 | 39 |
| Index-adjacent but nonphysical pairs | 58 | not reported |
| Start/end markers | 740/740 | 772/772 |

Differences in block IDs: **68 ZL3b-only**, **100 IT2a-only**, **672 common blocks**. The original unscoped pair-ID comparison found 50 ZL3b-only and 76 IT2a-only pairs; this was superseded by the corrected block-scoped pair identity. Under the corrected comparison: **384 ZL3b-only**, **410 IT2a-only**, **2,897 common pairs within identical blocks**. The old pair figures must not be treated as a validated block-aware mapping. These counts come from the aggregate audit, not from an independently verified alignment. ZL3b token/type counts are **35,492 / 6,980** under the canonical RC1.2 parser. IT2a token/type parity was **not checked**.

The audit reports `ZL3b_structure_verified=true`, `IT2a_structural_pair_mapping_identical=false`, `IT2a_token_matching_verified=false`, `gate_ready=false`. The workflow job's `SUCCESS` means that the audit ran successfully and exported evidence; **it does not mean W47 can execute**.

## Required reconciliation, without weakening the frozen protocol

1. Independently reproduce and attest the ZL3b block/locus/first-word parsing against RC1.2 with complete difference register and immutable hashes.
2. Investigate and account for the 13 ZL3b P loci outside structural blocks, the nonphysical adjacency category, and all cross-transcription block/pair discrepancies; do not silently drop or join them.
3. Attest a **training-only** common folio mapping and pair eligibility for ZL3b and IT2a. Same manuscript, so this is a sensitivity comparison, not independent replication.
4. Produce a verified parser evidence report, approved isolated runner and input-isolation evidence before changing `gate.json` from `PENDING`. The preflight and scientific experiment remain blocked.

Separate CI failure: run [43866019316](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866019316) fails because `001-paragraph-header-key` lacks `attempt.yml`; log says `NON VERIFICATO`. Preserve the explicit legacy exception/quarantine; do not invent a contract or silently bypass verifier checks.

**Decision: NOT READY / PENDING EVIDENCE.** No scientific result is inferred from this structural report.

## Artifact and provenance check for run 43866559030

The original GitHub artifact was downloaded and checked against the Actions artifact API digest: `w47-structural-audit.zip`, **SHA-256 `979db3667b15a74b24bb98fb4af4fc3b94f274d981a36adb2b44651daf5a577b`**. The archive contains only `w47-structural-audit.json` (2,553 bytes). Its workflow provenance identifies run `43866559030`, branch `research/week47-qo-rivals-plan-20261116`, head commit `85d2ba676d7d98918e3d40dc33f6bac4faa2d9fc`; the job concluded `success`. The source and parser hashes recorded in the JSON match the canonical digests listed above.

Aggregate arithmetic checks pass: 672 common blocks + 68 ZL3b-only = 740; 672 + 100 IT2a-only = 772; 2,897 shared pairs + 384 ZL3b-only = 3,281; and 2,897 + 410 IT2a-only = 3,307. ZL3b also reports 4,117 loci in blocks + 13 outside = 4,130. These checks establish consistency of the archived aggregates, **not** correctness of an independent parser-to-locus mapping.

**Scope limitation:** the archived audit is full-corpus structural output and contains aggregate hashes rather than the underlying per-locus/block mapping. I did not rerun it or inspect any corpus or protected-page content. It cannot satisfy a holdout-safe independent mapping audit, and it does not establish IT2a token parity. Keep `parser_evidence.status = PENDING` and `input_isolation = PENDING` in `gate.json`.

## Remaining gate conditions

The frozen `NULL_ONLY` preflight remains blocked until all of these are evidenced on commits preceding any dispatch:

1. **Parser evidence:** an independently reviewed, hash-bound report of the canonical parser, full ZL3b block/locus/token/adjacency alignment and IT2a correspondence, including explanations for the 13 out-of-block loci and the 384/410 pair differences. Existing aggregate hashes/counts are insufficient; no reserved sample may be opened or analyzed to produce this evidence.
2. **Runner approval:** `run_locked.py` is present on the branch, but `gate.json` has no approved-runner commit/hash and the runner has not passed an independent code/isolation review. It must remain unapproved until that review completes.
3. **Input isolation:** a verifiable training-only input manifest and audit showing that the analysis workspace contains neither original full corpora nor protected inventory. The current gate value is `PENDING`.

For this `NULL_ONLY` question, `rivals.status = NOT_APPLICABLE_NULL_ONLY` is already the frozen choice; no Timm–Schinner rival is required. Passing synthetic CI is not a substitute for any of the three conditions and does not authorize dispatch. No protocol, baseline, gate value, or `main` branch was changed here.

## Synthetic verifier correction (16 November 2026)

Review found that `compare_structural_manifests.py` could return `MATCH` for identical manifests with dangling locus-to-block references, cross-page block assignments, or dangling/nonphysical next-locus references. It also raised an unstructured exception for a non-object top-level manifest. The comparator now rejects these conditions, and `tests/test_week47_manifest_compare.py` has synthetic-only regressions. No manuscript data was supplied to or read by this comparator. Local checks: 15 comparator tests PASS; RC1.2's built-in synthetic unit checks PASS. GitHub Actions status and commit are recorded after the change is pushed; these checks do not promote parser evidence or the scientific gate.

## Updated evidence, run 43866559030

Artifact [14226800088](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866559030/artifacts/14226800088): all 13 ZL3b P loci outside blocks have a nonempty first word and lack both an opening and closing marker on their own line. This does **not** prove the reason for their exclusion. The updated comparison scopes pair identity to the containing block and gives 384 ZL3b-only, 410 IT2a-only, 2,897 shared pairs; the former 50/76 comparison did not include block identity and is superseded. No scientific gate is changed.
