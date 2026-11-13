# SEM-01 Image-only coding rubric v0.1 (DRAFT; no manuscript text)
Date: 2026-11-13. This rubric is an operational definition, **not** an assertion of historical meaning, plant identity, or a validated ANCHOR.

## Unit and eligibility
Unit: one folio-side illustration region, using a source image URL/IIIF canvas ID, region coordinates, image revision and independent annotator ID. Do not show transcriptions, transliterations, page text or textual annotations to coders. Images may contain original manuscript writing; mask text regions where feasible, documenting masking and image quality. Multi-panel regions are separately coded but linked to one folio-level group; no split across partitions.

## Categories (multi-label binary, each 1/0/uncertain/not-visible)
- **botanical morphology**: root-like organ, stem/trunk, leaf-like organ, flower-like organ, fruit/seed-like organ.
- **zodiac/astral iconography**: animal figure, human figure, radial arrangement, star-like motif, circular band.
- **pharmaceutical/material culture**: vessel/container, lid/stopper, tube/pipe, liquid depiction, apparent pouring/transfer.
- **procedural composition**: numbered/ordered visual stages (only if visually explicit), repeated units, connected channels, juxtaposed panels.
- **image quality**: legibility (good/partial/poor), cropping (yes/no), restoration uncertainty (yes/no).

These are visual features, not semantic translations. A vessel-like shape does not prove pharmacy; a star-like shape does not prove astrology.

## Annotation schema (one JSONL record per region and coder)
`{"folio_key":"...", "region_id":"...", "canvas_id":"...", "source_url":"...", "region_xywh":[0,0,0,0], "image_sha256":"...", "annotator_id":"...", "blind_to_transcription":true, "text_masked":true, "categories":{"root_like":"uncertain"}, "quality":{"legibility":"partial","cropped":false}, "notes_visual_only":""}`
The example is schema illustration only, not real data. Never store private identity or personally identifying annotator details; use pseudonyms.

## Two-coder adjudication
Two independent coders first; preserve both raw records. For each binary category calculate observed agreement, prevalence, Cohen kappa when defined; report denominator and undefined kappa explicitly. Adjudication is separate and blinded to text, with disagreement and uncertainty retained. Do not silently convert uncertain to 0. Thresholds and exclusion rules must be frozen before statistical testing.

## Negative-control annotations
A third coder receives shuffled images with region IDs removed; compare consistency. A separate batch receives crops with visual motifs obscured to assess reliance on page composition. Neither batch sees Voynich text.

## Evidence integrity
For each image capture: repository/source, original canvas ID, retrieval date, crop coordinates, raw bytes SHA-256, masked derivative SHA-256, and licensing/reuse note. Store original and derivative checksums separately. Verify image/folio alignment and all duplicate Yale canvas mappings before joining text. Do not treat the 42 noncanonical Library-reader extracts as original evidence.

## Fail-closed gates
No real manuscript semantic test until (1) source images and hashes independently verified, (2) coders blinded, (3) folio split privately secured, (4) category eligibility and sample size fixed, (5) independent ZL3b/IT2a mapping and transcription controls, (6) numeric death criterion and multiple-testing family frozen. A completed coding rubric is not a qualifying scientific attempt.

## Status
PROTOCOL_ONLY, NO IMAGE ANNOTATIONS, NO RUN, NO CLAIM OF DECIPHERMENT. Frozen RC1.4.2, RP-01, f085v and ANCHOR staging unchanged.
