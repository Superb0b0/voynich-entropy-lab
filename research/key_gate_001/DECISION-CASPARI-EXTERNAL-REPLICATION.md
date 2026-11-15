# DECISION KEY-GATE-001 / Caspari-Faccini: stop bespoke reconstruction, audit existing replication

Date: 2026-11-15
Classification: COMPARATIVE
Status: EXTERNAL_REPLICATION_REPORTED; LOCAL_REPLICATION_NOT_RUN
Verdict on Italian shorthand claim: NOT CONFIRMED by an external published test; project-level status remains REPLICATION_PENDING because we have not independently rerun its package.

## New primary-source audit
The original paper's Methods section states that the authors used a discursive process (including discussion by messaging apps), revised readings using word and illustration context, and that many lexical identifications remain ambiguous (PDF lines 303-312). The paper does not specify a deterministic executable algorithm for contraction, vowel insertion, truncation, or contextual resolution. It also states it does not use EVA and regards segmentation/alignment in EVA and v101 as potentially problematic (lines 274-276). The authors call their key preliminary and subject to substantial correction (lines 298-302).

## Independent external evaluation located
V. Averyanov's public evaluation reports reconstructing the candidate from the authors' addressed examples in EVA and testing the full manuscript under the stated shorthand freedoms:
- strict dictionary matching: 17.5% candidate vs 1.2% typical random key;
- permissive vowel-insertion/truncation lexical coverage: 69.7% real Italian vs 67.9% within-word shuffled pseudo-Italian;
- matched-volume Latin comparison: 90.3% vs 65.8% Italian.
The article says scripts/data are in a public replication package: https://voynich.site/files/voynich_replication_v1.zip (3.0 MB, 226 files, according to https://voynich.site/publications?lang=en).
Sources:
- https://voynich.site/en/hypotheses/caspari-faccini-key/
- https://voynich.site/publications?lang=en
These are external reported values; our repository has NOT downloaded or independently rerun the package. They materially undermine the Italian identification, but do not themselves prove the entire hypothesis class false.

## Technical correction to our work
1. Do not expand our 7-symbol toy bijection generator into a claimed matched null for Caspari-Faccini.
2. The 29-entry transcription of the paper's Table 1 is a visual-description transcription only; some glyph images are not machine-represented by the extracted PDF text. It is not a verified visual catalogue.
3. The example-derived EVA mapping is a separate third-party reconstruction, not the authors' glyph table.
4. Since the original authors' method is discursive and context-revised, exact equal-adaptation controls cannot be asserted until the search/fitting procedure is operationally specified. A bespoke reconstruction risks inventing rules not in the paper.

## Decision
Suspend further implementation effort on Caspari-Faccini as the main candidate. Preserve it as EXTERNALLY_CHALLENGED / NOT_CONFIRMED. Do not call it disproved in every possible formulation. Do not promote the external article's proposed verbose-homophonic alternative as a decipherment.

## Next admissible work
Acquire and inspect the published 226-file replication package; identify its source files, code, inputs, license and exact rule implementations; reproduce the published numerical checks in a clean, isolated environment using only public training data and no protected holdout. If package acquisition is unavailable, record the specific access blocker and do not substitute invented code. In parallel, compare at least one materially different cipher/encoding family using an identical, preregistered calibration protocol, not ad-hoc candidate readings.
