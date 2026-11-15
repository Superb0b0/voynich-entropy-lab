# KEY-GATE-001 candidate admissibility audit

Date: 2026-11-15
Branch: research/private-training-preflight-20261115
Classification: COMPARATIVE / STRUCTURAL
Verdict: NON VERIFICABILE (candidate not admissible; no negative decipherment result)

## Candidate examined
DECIPHER-CANDIDATE-001, Caspari–Faccini, as described in the repository's existing candidate note. The published proposal is an image-derived Italian shorthand/cipher with glyph-to-letter correspondences, ligatures and expansions. The repository note explicitly records that no independently audited glyph-to-EVA alignment, locked machine-readable key, blind reading or held-out translation exists.

## Why rival equivalence cannot yet be demonstrated
A rival family must be conditioned on the actual candidate's formal transformation grammar and fitting procedure. At present the project has no machine-readable candidate key and no independently checked correspondence between the paper's glyph units and the chosen transcription units. Therefore the following are unknown, not zero:
- exact input symbol inventory and segmentation;
- mapping cardinalities and many-to-one/one-to-many rules;
- null, ambiguity and abbreviation budgets;
- allowed vowel insertion, truncation, ligature expansion and contextual operations;
- fitting objective, search algorithm, initialization, iteration budget and stopping rule;
- complete provenance of loci consulted while constructing the published key.

Generating random bijections or 999 toy substitutions would not match these freedoms. It would create an invalid null comparison. The 7-symbol exhaustive toy class is only a combinatorial software test and is excluded from scientific evidence.

## Gate decisions
- Candidate eligibility: FAIL (required machine-readable key and audited glyph/transcription alignment absent). This is an eligibility failure, not falsification of the historical hypothesis.
- Matched rival construction: NON VERIFICABILE (candidate grammar and fitting procedure absent).
- Language scoring: NON VERIFICABILE (no frozen historical-language corpus/model manifest in this project).
- Holdout evaluation: NOT RUN; protected material remains unopened.
- Independent reproduction: NOT RUN.
- Decipherment: NOT ESTABLISHED.

## Required next evidence
1. Extract the authors' complete glyph table and all transformation/exception rules into a machine-readable specification, with exact source page/table citations.
2. Independently align every key glyph to manuscript glyph instances and a declared transcription edition; mark uncertain correspondences rather than guessing.
3. Recover and freeze the authors' complete construction/fitting procedure and provenance. If it cannot be recovered, the published candidate cannot be fairly tested under an equal-adaptation claim.
4. Only then define the null generator by applying the same allowed operations, search procedure, objective and compute budget to randomized mappings; audit exchangeability on synthetic known-plaintext controls.
5. Freeze language model and evaluator, obtain independent code review, then consider a single protected evaluation under the existing access rules.

## Non-claim
No 999-key scientific comparison has been performed. No PASS or FAIL about Voynich decipherment is warranted. The only supported conclusion is that the current candidate representation is insufficient to construct a valid matched-control experiment.
