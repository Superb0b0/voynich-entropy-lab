# QO-RIVAL-01/02 CORRECTION — page-side collision

Date: 2026-11-13. Status: **CORRECTION / EXPLORATORY, NOT VALIDATED**.

The earlier local implementations grouped records by `(leaf_number, paragraph_index)`. Recto and verso of the same leaf could therefore be merged. **Previous numerical claims 28/272 (10.29%), 115 groups, and 59/59 leave-one-folio-out must not be used as validated or reliable findings.** The earlier QO-RIVAL-02 leave-one-out claim is withdrawn pending re-execution on corrected groups.

Independent corrected implementation groups by `(full_page_id, paragraph_index)`, retaining leaf ID only for holdout exclusion and leaf-level shuffle.

Input `data/ZL3b-n.txt` SHA-256 verified locally: `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`. Held-out leaf IDs excluded from statistics.

Corrected exploratory training results, 2,000 permutations per null, seed 20261113:
- 211 paragraph groups
- observed qo→qo 14/396 = **0.03535353535**
- within-paragraph shuffle null mean **0.1648565976**, depletion Monte Carlo p **0.0004997501**
- within-leaf shuffle null mean **0.1717863588**, depletion Monte Carlo p **0.0004997501**
- Holm adjusted p across two nulls **0.0009995002** each.

**Limitations**: The parser still needs reconciliation with canonical RC1.x pipeline; paragraph-start and adjacency semantics may be incorrect. This is post-hoc correction, not new independent confirmation. The nulls are simple shuffles, not full text generators. No holdout evidence and no decipherment claim. The corrected local script is available as `qo_rival_page_corrected.py` in the chat artifact, not asserted to have run in GitHub CI.

The previous `research/qo-rival-01-local-results.md` and `research/qo-rival-02-leave-one-folio-out.md` are superseded by this correction.
