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
2. **Training preparer provenance:** independently review `training_preflight.py`, record its commit/hash, and verify that its output is confined to authorized training inputs.
3. **Partition policy provenance:** independently audit the protected-page exclusion policy without disclosing its identifiers; record its commit/hash and confirm that the training split is the authorized one.
4. **Runner approval:** `run_locked.py` is present on the branch, but `gate.json` has no approved-runner commit/hash and the runner has not passed an independent code/isolation review. It must remain unapproved until that review completes.
5. **Input isolation:** a verifiable training-only input manifest and audit showing that the analysis workspace contains neither original full corpora nor protected inventory. The current gate value is `PENDING`.

For this `NULL_ONLY` question, `rivals.status = NOT_APPLICABLE_NULL_ONLY` is already the frozen choice; no Timm–Schinner rival is required. Passing synthetic CI is not a substitute for any of the five conditions and does not authorize dispatch. No protocol, baseline, gate value, or `main` branch was changed here.

## Synthetic verifier correction (16 November 2026)

Review found that `compare_structural_manifests.py` could return `MATCH` for identical manifests with dangling locus-to-block references, cross-page block assignments, or dangling/nonphysical next-locus references. It also raised an unstructured exception for a non-object top-level manifest. The comparator now rejects these conditions, and `tests/test_week47_manifest_compare.py` has synthetic-only regressions. No manuscript data was supplied to or read by this comparator. Local checks: 15 comparator tests PASS; RC1.2's built-in synthetic unit checks PASS. Source change: commit `485f5e674054f6dc5ada27cb1c1014d57195ffe7`; regressions: `0975dd0887f9139949e4a25012fbc4d587cffded`.

GitHub Actions [run 43869742325](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869742325) is **SUCCESS** for `guard-tests`, including the 15 synthetic comparator tests, the existing synthetic preflight/runner tests, and the negative preflight refusal. `preflight`, `prepare-input`, and `experiment` were **SKIPPED**. This confirms the code correction only; it is not a parser parity result or a scientific run.

Separate training-only structural evidence is available in [run 43869742384](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869742384), artifact ID `14227136003`, archive SHA-256 `a13ad391f46c44c4e29eb6fa6852df244d31eeac9997f7a59cf7373fbcfb0ad3`. The aggregate says status `TRAINING_STRUCTURE_ONLY_NOT_SCIENTIFIC`: 548 common blocks, 521 exactly aligned A/B blocks, 2,241 common pairs, and 75 represented physical folios; the artifact contains no words or folio identifiers. Its verify job ran on a separate workspace without original corpora or `HOLDOUT.md`. The preparer reads the original files to hash and filter them; the independent provenance of that preparation and its exclusion policy remains PENDING, so these counts do not close the gate.

The current branch head also records [run 43869742449](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869742449) as a general-verifier **FAIL** for legacy attempt 001 missing `attempt.yml`. This remains visible and is unrelated to the synthetic comparator fix.

## Updated evidence, run 43866559030

Artifact [14226800088](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866559030/artifacts/14226800088): all 13 ZL3b P loci outside blocks have a nonempty first word and lack both an opening and closing marker on their own line. This does **not** prove the reason for their exclusion. The updated comparison scopes pair identity to the containing block and gives 384 ZL3b-only, 410 IT2a-only, 2,897 shared pairs; the former 50/76 comparison did not include block identity and is superseded. No scientific gate is changed.


## Supplementary parity JSON reviewed (16 November 2026)

Two Library files, `W47_canonical_parity_report.json` and `W47_canonical_parity_report(1).json`, contain identical 1,711-byte JSON. They claim ZL3b status `VERIFIED`, 0 token mismatches, 0 block-boundary mismatches, 740 matched blocks and 4,130 matched loci, and repeat the canonical corpus/parser SHA-256 values. Their own limitations say `matched_pair_eligibility=false` and `it2a_pair_mapping_checked=false`; the report also says the full corpus was read only for structural/token parity. The duplicate is not an independent corroboration.

The JSON is not tied to a repository commit, workflow run, audit-script SHA, or retrievable per-locus/block manifests in this record. Its `adjacency_mismatches=0` field therefore does not establish pair-eligibility parity, and its `VERIFIED` label cannot satisfy the fail-closed preflight. I did not rerun the full-corpus check or inspect corpus/protected-page content. Treat this as a reported aggregate, not a gate attestation; parser/mapping and IT2a gates remain `PENDING`.


## Synthetic RC1.2 mapping check (16 November 2026)

Added two corpus-free cases to `tests/test_week47_manifest_compare.py`: canonical locus/folio/line-index mapping with header line offsets, `fRos`, and token cleaning for braces/square alternatives; and fail-closed rejection of a malformed locus ID. Local focused run: 17 tests **PASS**. The square-alternative fixture confirms RC1.2 outputs two surviving tokens (`zha`, `o`), which is now asserted explicitly. Commit: `4043a2e31afde57f5d19c3ae3d8653a95a4f1887`.

No workflow run or commit status is attached to this commit at report time. The available GitHub Actions interface here exposes run lookup/rerun but not workflow dispatch; therefore remote CI for this added fixture is **PENDING**. This synthetic check does not verify full-corpus locus mapping, parser provenance, or ZL3b/IT2a parity. The scientific gate remains **PENDING**.


## Reproducible structural replay (16 November 2026)

Replayed the committed `structural_audit.py` at the current PR head (`857994f6d6123c596843c6145f06a0bb1fe93afb`); the remote file is byte-identical to the local source (SHA-256 `06a4ea83a76a75e5ce34a12f9cbeee8505eb5f6ca76ca43a721efd0dfb0e4dc3`). Input SHA-256 checks passed: ZL3b `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; IT2a `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`; parser RC1.2 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`. ZL3b RC1.2 census passed exactly (4,130 loci, 35,492 tokens, 6,980 types); all 4,130 loci were compared per-locus to the historical token cleaner with zero mismatches. Structure is 740 blocks, 4,117 P loci inside and 13 outside. IT2a is 772 blocks and 4,118 P loci; only structural/pair mapping was checked, not token parity. Across transcriptions: 672 identical blocks, 2,897 eligible pairs in common blocks, 384 ZL3b-only and 410 IT2a-only pairs; no Currier disagreement on common blocks.

Aggregate-only replay output SHA-256: `ecdc8094d8899b3dc52648a88a34f16701a94cb4cc6ded4b0fd7c49fbff48012`. Its per-locus, block-boundary and pair-eligibility manifest fingerprints are ZL3b `2135a122bf886f8870fb7e32f4f0626cc49ca679d48a9df8cec252e60c123501`, `d445e11dcf778266cc5f49a009965a1a703cf91555a4f29bf8d74ad1ad95072a`, `a56832960571da83c6f76bcc7d176f2ab8a7c503e6dcea55932f0432175b80b4`; IT2a `630d90511ab8f04dcf139e45cbc7d5a751e5a0ced29b27b19dd036829f6d5140`, `f0a92983ac48fd3263878e48642dbb39c0a252c84b8c8b23f0fe13a5ed649dd3`, `529106f0e044301dffc94348202822ff3ff6596c7ec010a93a29b17ce2405aaf`. The output contains no locus/page IDs or text. Reproduction command: `python research/week47-qo-decision/structural_audit.py --zl3b data/ZL3b-n.txt --it2a data/IT2a-n.txt --parser experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py --out /tmp/w47-structural-audit-repro.json`.

Classification remains **structural only**, not a holdout evaluation or scientific result. It does not establish IT2a token parity, independent review of parser/source provenance, or training isolation. `gate_ready=false` remains unchanged. The matching historical Actions aggregate for run 43866559030 remains independently hash-verified as described above; this local replay establishes reproducibility of the current script and inputs, not independent code review. No workflow was launched by this replay.


## GitHub Actions after replay and CI fix (16 November 2026)

The first run on the new synthetic parser-mapping tests, [gated run 43878313479](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43878313479), exposed a CI checkout defect: the guard job's sparse checkout omitted the RC1.2 parser source, so the test module raised `FileNotFoundError` before the parser fixtures ran. The existing preflight and primitive synthetic suites passed; no scientific jobs ran. Fixed only the guard job's sparse-checkout list to include `experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py` (no corpus input). Fix commit: `d1716215926801630c0c76beb1532ebc239bb804`.

On the fix commit, [gated run 43878484575](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43878484575) is **SUCCESS**: guard tests pass, while preflight, prepare-input and experiment are **SKIPPED**. [Structural run 43878485102](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43878485102) is **SUCCESS**. [Training-only geometry run 43878484823](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43878484823) is **SUCCESS**: synthetic filtering, training preparation, and separate-workspace geometry verification all pass; its verification step confirms original corpora and protected inventory are absent from the evaluation job. These are technical checks, not a scientific run or validation.

The contemporaneous general archived-attempt verifier, [run 43878484701](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43878484701), remains **FAIL** for legacy attempt `001-paragraph-header-key` missing `attempt.yml`; its verifier regression tests pass. This is unrelated to the W47 checks and is not suppressed or waived. `gate.json` stays **PENDING**. No holdout endpoint, experiment, protocol, baseline, or `main` change occurred.
