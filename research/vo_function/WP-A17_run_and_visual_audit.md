# WP-A17 — Wellcome MS.22 image audit and comparative visual matrix

Date: 16 November 2026  
State: DOCUMENTARY / SINGLE-READER DESCRIPTIVE; no experiment and no Voynich corpus access.

## Evidence chain

- Institutional record: Wellcome Collection, [Alchemy: 15th cent. (MS.22)](https://wellcomecollection.org/works/ugn23v6p). It describes 106 leaves, an Italian alchemical receipt collection, instructions concerning medicines, quintessences and distillations, and **12 carefully executed pen-drawings of alchemical apparatus**. The record does not provide folio-by-folio locations for those 12 drawings.
- Institutional IIIF Presentation v2 manifest: https://iiif.wellcomecollection.org/presentation/v2/b19480271 ; SHA-256 `1672e82e656b7ff66cf678d4c69f509fc35b9df7d04cb6bd5f705d96487fcf7c`; 228 canvases. Canvas labels are metadata; they are not, by themselves, independent folio authentication.
- User-specified acquisition run #43867283581 succeeded. Its artifact #14225058611 ZIP SHA-256 is `e7c575edf5fb80d27aeb52d76a654f7a24a580bfbc0a011d72a9ee0d9928e8e8`; checked locally against the artifact digest. It contains 13 fixed-spaced internal preview JPEGs, image reports, manifest and canvas inventory. The 13 previews were opened and inspected; all are JPEG, and their SHA-256 values match the report.
- Follow-up PR run #43869535689 succeeded after adding full-resolution acquisition for visually flagged candidates. Artifact #14227285659 ZIP is 39,815,556 bytes; SHA-256 `be347e15d7c090ce42ddc31404f7e65e022fcc1e770d8312d3caef1223149c96`. This digest was independently recomputed on the downloaded ZIP. Artifact has 46 files including 16 full-resolution candidate JPEGs; all 16 JPEG signatures, lengths and per-image SHA-256 values match the included `apparatus_candidate_fetch_report.json`.
- Candidate canvases flagged in a visual sweep of all 228 preview canvases: 146 (70v), 148 (71v), 154 (74v), 156 (75v), 160 (77v), 161 (78r), 163 (79r), 164 (79v), 167 (81r), 177 (86r), 179 (87r), 186 (90v), 192 (93v), 210 (102v), 212 (103v), 213 (104r). These are **visual candidate pages**, not an institutional page list for exactly 12 drawings; some are faint or could be vessel-like sketches rather than one of the catalogued apparatus drawings. No page reference has been invented. Exact mapping of the 12 catalogue-described drawings to folios remains **NOT VERIFIABLE** from the institutional record currently available.
- The earlier 13-image feasibility selection is separate: 2r, 11r, 20r, 29r, 38r, 47r, 56r, 65r, 74r, 83r, 92r, 101r, 106r. It is a fixed-spaced feasibility sample, not representative and not designed to locate apparatus.

## Visual matrix

The CSV `visual_matrix_wellcome_ms22.csv` contains V01–V14 and R01–R04 fields for 16 MS.22 candidate canvases and 13 spaced-preview canvases. It also carries the previously recorded Sloane MS 4016 single-reader codes (V01/V04/V11 only) and a Fitzwilliam MS 251 row with NA for every visual code because this run did not acquire or inspect its images.

- V values use the unchanged WP-A3 codebook. 0 means not visible in the inspected image; 1 means visible; U means ambiguous; NA means not assessed/not available.
- Apparatus identity is never inferred from a vessel outline. Candidate marks are described as visible forms only.
- R03 is NA because a pairwise adjacent-folio coding pass was not completed. Other uncertain relational judgments are kept U.
- The matrix is one reader, exploratory and not independently validated. It is not a significance test, classifier, or text–image coupling analysis.

## Descriptive comparison

| Witness | What the institutional source establishes | What the inspected visual sample establishes | Limitation |
|---|---|---|---|
| Wellcome MS.22 | Late 15th century; Italian; alchemical receipts; 12 apparatus drawings; 106 leaves; 228 digital images | The 13 spaced previews include largely text pages and a sparse diagram; the visual sweep flags 16 candidate pages with vessel/apparatus-like line drawings | Catalogue does not locate the 12 drawings by folio. Candidate set is post-viewing and not representative. |
| BL Sloane MS 4016 | c.1440 Lombard herbal with digitised coverage | Prior WP-A12 inspection of ten endpoints/extreme folios recorded whole plants on 8/10, human figures on 2/10, and short adjacent labels on 8/10 | Prior one-reader matrix was formally coded only for V01, V04 and V11; remaining fields stay NA here. |
| Fitzwilliam MS 251 | Paris, c.1415; French illustrated encyclopaedia translated from Bartholomew the Englishman; museum provides selected folio pages | No image was acquired/coded in this run | Partial, curated institutional access; visual matrix intentionally all NA. |

This is descriptive context only. A readable operational recipe manuscript and illustrated herbals/encyclopaedias show that images and procedural text coexisted in different genres. No similarity to the Voynich, semantic identification, or functional conclusion follows from this comparison.

## CI and scope

- Documentary acquisition workflow: **PASS**, run [#43869535689](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869535689).
- General archived-attempt verifier: **FAIL**, run [#43869535451](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869535451), exact existing blocker: `001-paragraph-header-key: missing attempt.yml; cannot infer execution contract`. This was not bypassed or changed.
- No Voynich experiment, no holdout access, no corpus or canonical parser changes, no merge to main. RC1.4.2/V7.1 remains CLOSED_PENDING_VALIDATION.
