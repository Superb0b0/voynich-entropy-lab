# SEM-01: image–text semantic anchor, preregistration DRAFT (2026-11-13)

**Status: PROTOCOL_ONLY / NOT EXECUTED / NOT QUALIFYING.** This is a proposed falsifiable semantic test, not a claim of translation or botanical identification. Freeze the protocol, independently curate reference labels, and verify source hashes *before* any run. No access to historical/public holdout, and no alteration of RC1.4.2 or ANCHOR staging.

## Explanatory rivals
- **H-L (lexical / nomenclator):** repeated text forms adjacent to independently identified illustrations map consistently to semantic categories or referents across folios, beyond scribal/section/layout effects.
- **H-G (generative / positional):** forms are determined by local spelling, position, line geometry, section and Currier regime; apparent image associations vanish under controls.
- **H-C (cipher / encoded natural language):** associations may exist but should be tested after *independently specified* transformations, not after choosing a cipher by fitting these labels.
- **H-M (mnemonic/procedural):** local text order predicts independently coded visual operations or diagram relationships more than plant species identities.

## Independent semantic anchors
Use **only** visual labels created without seeing Voynich transcription, and independently double-coded by two experts. Separate botanical morphology (root/leaf/flower), zodiac sign iconography, pharmaceutical container shapes and page composition; do not conflate a modern taxonomic guess with a historical identification. Record inter-rater agreement, provenance, missingness and image quality. Existing ANCHOR-01/02/03/04 are *candidate evidence*, not validated ground truth; do not treat their unverified Library text-reader copies as byte-canonical.

## Split and leakage
One training partition of folios, and a *separately secured* private validation partition maintained by an external custodian. Do not generate a public HOLDOUT.md or embed reserved IDs in scripts. Any previously inspected public holdout is historical only. Stratify prospective evaluation by section, Currier A/B, hand, quire and page type where support permits; never let text from the same folio cross train/test. Keep related multipanel pages together.

## Predeclared primary endpoint (to freeze once data available)
Out-of-folio cross-entropy improvement for a multinomial classifier predicting independently annotated visual **morphology category** from text features versus a rival classifier with only folio-external covariates (section, Currier, hand, layout, line length, transcription). Fixed candidate vocabulary, regularization and folds before evaluation. Null: permutation of visual labels at folio level *within the prespecified eligible strata*, with 20,000 draws and fixed published seed. Holm correction across morphology, zodiac and vessel families. Negative controls: (1) shifted labels between matched folios; (2) text from distant regions; (3) randomized glyph strings preserving length and first-two-character frequencies. Evaluate ZL3b and IT2a with a fixed alignment policy and report discordant loci.

**Death criteria, to finalize numerically before execution:** reject semantic lexical hypothesis if out-of-folio improvement <= 0 or not robust in both transcriptions and matched negative controls; any insufficient matched strata yields INCONCLUSIVE, never a post-hoc pooled p-value. No semantic assignment or decipherment may be inferred from a classifier alone.

## Execution blockers
Independent blind visual annotation file with provenance and hashes is not yet verified; private replacement holdout custodian is not established; morphology label ontology and exact eligibility thresholds must be frozen. Therefore do **not** run on real text or count as qualifying. Next action: build independent image-only annotation and ontology with no transcription exposure, then preregister numeric gates and run calibration on synthetic matched confounds.

## Provenance
Repository source-of-truth consulted: main PROTOCOL.md, LOG.md, KNOWLEDGE.md, STATE.md, TESTS.md and anchor-rev3-staging-20261112 anchor/evidence-rev3/README.md, anchor/TRANSFER_STATUS_20261112.json. Staging manifest warns 42 Library-reader extracts are noncanonical. This document is a new proposal, not an ANCHOR revision.
