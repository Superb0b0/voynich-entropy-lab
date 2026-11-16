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

## Updated evidence, run 43866559030

Artifact [14226800088](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866559030/artifacts/14226800088): all 13 ZL3b P loci outside blocks have a nonempty first word and lack both an opening and closing marker on their own line. This does **not** prove the reason for their exclusion. The updated comparison scopes pair identity to the containing block and gives 384 ZL3b-only, 410 IT2a-only, 2,897 shared pairs; the former 50/76 comparison did not include block identity and is superseded. No scientific gate is changed.
