# Correction to partial Caspari-Faccini reconstruction

The earlier file `caspari_faccini_partial_key.json` contains an example-derived EVA-string mapping (e.g. d=T, ch=P) and must NOT be mistaken for the complete glyph table published by Caspari and Faccini.

The source paper's Table 1 instead defines visual glyph descriptions and proposed Latin values (e.g. ꝛ=A, ꝑ=B, ꝓ=C, ꝗ=D, 9=E, 8=T), with ligatures and special forms. The authors explicitly state that they do not use EVA and argue that EVA may split or merge glyph units incorrectly.

The authoritative transcription of the paper's Table 1 for this project is now:
`caspari_faccini_glyph_table_v1.json`.

The example-derived EVA correspondences are a separate, partial compatibility reconstruction published by a third-party evaluator, not the authors' complete key and not a verified glyph-to-EVA map. Keep it separate. Do not merge the two tables or treat either as a complete executable key.

The source paper's own Methods section (PDF lines 303-312) says the authors used a discursive process, revised readings in context, and that many word identifications remain ambiguous. It does not specify an executable deterministic grammar for vowel insertion, final truncation, or contextual choices.

Consequently, the candidate remains INELIGIBLE_FOR_CONFIRMATORY_TEST. This is a documented specification gap, not a falsification of every possible Italian hypothesis.
