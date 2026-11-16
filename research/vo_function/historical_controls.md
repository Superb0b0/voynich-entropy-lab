# VOY-FUNCTION-01: matched historical controls (WP-A14)

Status: DOCUMENTARY CONTROLS SELECTED, NOT VISUALLY CODED. 2026-11-16.

## Positive operational control: Wellcome Collection MS.22
- Primary catalogue: https://wellcomecollection.org/works/akn92u5z
- Digital viewer: https://wellcomecollection.org/works/akn92u5z/items
- 15th-century Italian-language alchemical recipe manuscript, 106 leaves, **228 digital images**, Public Domain Mark.
- Institutional description explicitly documents directions for alchemical medicines, quintessences and distillations and **12 drawings of apparatus**.
- A *positive operational control* on external catalogued contents, **not** proof that every image contains apparatus or sequence. Image URLs/canvas IDs not yet inventoried or coded.
- Do not assume that the catalogue's 12 apparatus drawings represent 12 separate folios or that the 228 images correspond one-to-one to 228 text faces.

## Negative descriptive control: Fitzwilliam Museum MS 251
- Primary catalogue: https://fitzmuseum.cam.ac.uk/illuminated/manuscript/discover/jean-corbechon-livre-des-proprietes-des-choses
- French illustrated encyclopedia, Paris c.1415, translated from Bartholomaeus Anglicus, explanatory/descriptive, partial digitisation.
- Individual museum folio: https://qi.fitzmuseum.cam.ac.uk/illuminated/manuscript/discover/jean-corbechon-livre-des-proprietes-des-choses/section/undefined/folio/folio-166v
- Not a procedural control. Available museum folios are an accessibility-biased subset, not a random sample.

## Prior baseline: British Library Sloane MS 4016
- Ten JPEGs physically retrieved from run https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43865677456, artifact #14226090230.
- First single-reader V01–V14/R01–R04 visual matrix created outside repository; see issue #27 WP-A13. **Not independently validated**.

## Protocol before any comparison
1. Acquire Wellcome manifest/canvas metadata via its public catalogue/IIIF API and store manifest SHA, timestamp, canvas labels and image rights. Don't invent a manifest URL.
2. For MS.22 use separate strata: *catalogue-located apparatus drawings* and *non-apparatus pages*; catalogue-directed sampling is **targeted**, not representative. Record how apparatus folios were located.
3. For MS 251 first enumerate which folios have accessible museum images, then freeze selection rule; no pretending to have whole-volume coverage.
4. Visual codebook V01–V14 and R01–R04 unchanged, single-reader preliminary only; no significance tests, no Voynich visual-text coupling, no holdout.
5. Distinguish text-known operational status (from historically readable manuscripts) from image-coded observable apparatus, conduit, sequence, vessel. No semantic inference from ambiguous illustrations.

Research state remains RC1.4.2/V7.1 CLOSED_PENDING_VALIDATION.
