# QO-RIVAL-01: frozen exploratory protocol

Status: EXPLORATORY. Precommitted before any workflow execution. This is a **new null-model comparison**, not an independent replication of the previously selected qo effect.

Input: ZL3b-n.txt SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc. Holdout leaf IDs are excluded from every statistic; the complete source is read for checksum only.

Parser: IVTFF page headers and loci matching `[*@+=]P`; first word of each P line; contiguous numeric line IDs within the same paragraph. Compare first-word prefix `qo` across consecutive P lines. No post-hoc filters.

Two rival nulls, 2,000 permutations each, seed 20261113: (1) shuffle first words within each paragraph, preserving positions; (2) shuffle first words across paragraphs within each folio, preserving positions and folio inventory. One-sided depletion p=(1+count(null<=observed))/(2001), Holm across both tests. Report numerator and denominator.

Death criteria: no claim of depletion unless BOTH null-model Holm-adjusted p-values <=0.01; even if both pass, classify only as a training signal. A model which preserves exact qo transition structure is not tested. No interpretation as translation, language, or encryption. Any parsing failure or input checksum mismatch aborts. No holdout access for model selection.

No external API, no secrets, no repository write permissions; results are ephemeral GitHub Actions artifacts.
