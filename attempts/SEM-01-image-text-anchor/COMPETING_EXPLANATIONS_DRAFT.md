# SEM-01-03 — Semantic prediction matrix (DRAFT, NOT EXECUTED)
Date: 2026-11-13. Branch-only research proposal; does not use or disclose any holdout.

## Competing full explanations and *distinctive* predictions
| Hypothesis | Image–text prediction | Cross-section prediction | Strongest falsifier |
|---|---|---|---|
| L: ordinary language | blind image-only category predicts stable lexical families on unseen folios, after controlling section/hand/layout | inflection and syntax transfer across botanical, zodiac, pharmaceutical sections | image categories fail to predict forms out of folio and no consistent grammar survives transcription |
| C: enciphered natural language | a **predeclared** decoding family yields reusable words/grammar and independent iconographic matches | same key/rules transfer to new folios; ciphertext distribution differs by context only as predicted | key requires folio-specific retuning or fails blinded predictions |
| N: nomenclator / codebook | stable token-to-entity correspondences, low ambiguity within comparable illustrations | token reuse tracks independently identified referents across folios | token identities vary primarily with line position/hand and not entity |
| G: mechanically/artificially generated text | local glyph/line-position rules predict tokens better than visual semantics | transfer depends on scribal mechanics; image association disappears after matched controls | independent image classes predict stable token meanings after strong confound controls |
| M: mnemonic / procedural notation | sequences correlate with independently annotated **relations or ordered visual steps**, not modern species names | shared operation motifs align across diagram and vessel sections | no transfer of operation-to-token associations to unseen folios |

## Blind benchmark design
1. **Image-only**: two independent coders annotate visual morphology and ordered relations without transcription; resolve Yale canvas duplicates and region provenance. Record ambiguity rather than forcing identifications.
2. **Text-only**: a separate analyst freezes feature extraction, transcription policy and all model hyperparameters without viewing visual labels. Treat all old public holdout IDs as historical, not prospective independent evidence.
3. **Rival predictions**: before join, each model submits its predicted category probabilities for every eligible folio, and where applicable a token–meaning mapping or deterministic decoding algorithm. Baselines: section, Currier, hand, quire, folio geometry, length and text-only local Markov generator.
4. **Evaluation**: compare strictly out-of-folio log-loss and calibration to baselines; matched folio-level label permutations preserve section/hand/quire where feasible. Report uncertainty, effective strata, exclusions, all tested families and Holm correction. Fail closed on insufficient strata.
5. **Interpretation gate**: positive category prediction alone establishes association, not translation. A *decipherment* additionally requires a fixed reversible mapping that generalizes to independent unseen text, produces coherent grammar/semantics and agrees with external dated linguistic/iconographic evidence.

## Immediate blocker and non-duplicative next action
ANCHOR staging says most Library project materials and original images are not in the repo; 42 imported text files are noncanonical. Thus no image-label matrix with verified image SHA-256 is currently demonstrated. Obtain provenance-preserving image crops and blind coders before any scientific test. No simulated 'expert labels' allowed.

Status: **PROTOCOL_ONLY / NOT A QUALIFYING ATTEMPT / NO NEW VOYNICH RESULT**. Do not touch RC1.4.2 CLOSED_PENDING_VALIDATION, RP-01, f085v, frozen ANCHOR staging or public HOLDOUT.md.
