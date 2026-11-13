# QO-RIVAL-04 — corrected leave-one-leaf-out sensitivity

Date: 2026-11-13. **EXPLORATORY / POST-HOC / NOT VALIDATED**.

Input: `data/ZL3b-n.txt`, SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`, verified locally. Held-out leaf IDs excluded from metrics. Parser follows corrected full-page (recto/verso) grouping, but has **not** been independently reconciled with the RC1.x canonical parser.

- Training leaves represented: **78**; leaves contributing a qo-conditioned adjacent pair: **69**.
- Paragraph groups: **211**.
- Observed qo→qo: **14/396 = 3.535%**.
- Remove each of 78 training leaves in turn: **78/78** remaining datasets retain observed depletion relative to the corresponding Monte Carlo expected-count ratio for within-paragraph shuffles.
- Leave-one-out observed conditional rate range: **2.6954% to 3.6939%**.
- Leave-one-out expected null count-ratio range: **15.5985% to 16.8097%**.
- 2,000 within-paragraph shuffle iterations, seed **20261114**.
- This is a **directional sensitivity check**, not 78 independent hypothesis tests; no individual leave-one-out p-values are claimed.

The earlier 59/59 result in QO-RIVAL-02 was invalidated by recto/verso grouping collision; this replaces that claim. The present signal remains potentially sensitive to the parser's paragraph and adjacency conventions and to more realistic text-generation nulls. No decipherment or linguistic interpretation is supported yet.
