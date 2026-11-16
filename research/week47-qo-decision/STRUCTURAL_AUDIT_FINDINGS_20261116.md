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

Differences in block IDs: **68 ZL3b-only**, **100 IT2a-only**. Differences in strict eligible pair IDs: **50 ZL3b-only**, **76 IT2a-only**. These counts come from the aggregate audit, not from an independently verified alignment. ZL3b token/type counts are **35,492 / 6,980** under the canonical RC1.2 parser. IT2a token/type parity was **not checked**.

The audit reports `ZL3b_structure_verified=true`, `IT2a_structural_pair_mapping_identical=false`, `IT2a_token_matching_verified=false`, `gate_ready=false`. The workflow job's `SUCCESS` means that the audit ran successfully and exported evidence; **it does not mean W47 can execute**.

## Required reconciliation, without weakening the frozen protocol

1. Independently reproduce and attest the ZL3b block/locus/first-word parsing against RC1.2 with complete difference register and immutable hashes.
2. Investigate and account for the 13 ZL3b P loci outside structural blocks, the nonphysical adjacency category, and all cross-transcription block/pair discrepancies; do not silently drop or join them.
3. Attest a **training-only** common folio mapping and pair eligibility for ZL3b and IT2a. Same manuscript, so this is a sensitivity comparison, not independent replication.
4. Produce a verified parser evidence report, approved isolated runner and input-isolation evidence before changing `gate.json` from `PENDING`. The preflight and scientific experiment remain blocked.

Separate CI failure: run [43866019316](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866019316) fails because `001-paragraph-header-key` lacks `attempt.yml`; log says `NON VERIFICATO`. Preserve the explicit legacy exception/quarantine; do not invent a contract or silently bypass verifier checks.

**Decision: NOT READY / PENDING EVIDENCE.** No scientific result is inferred from this structural report.
