# ANCHOR01-INVENTORY-COHERENCE-01 (preregistered, synthetic negative control)

Question: Does the inventory silently accept mismatched filtered folio coverage across input transcriptions?

Observation prior to test: the current `attest` function intersects per-input page sets, so one-sided omissions can be silently hidden. This is a code-level observation, not evidence about the Voynich.

Prediction: a two-file synthetic fixture with a page missing from exactly one file MUST be rejected before writing output. An identical two-file fixture MUST pass. A protected page in either file MUST fail. A single-file fixture remains supported.

Rival: intersection is intentionally permitted to select only jointly covered pages. This is not acceptable for an attestation labelled as the full eligible inventory without an explicit declared coverage policy; a separate intersection mode would require its own frozen protocol.

Metric: exact binary outcome (exception and no output file vs successful attestation); criterion: 100% of three predeclared fixture outcomes. No p-value. No Voynich data, no holdout reads, no historical corpus SHA required for this code-level test. Python 3.11 stdlib unittest, deterministic, no random seed.

Decision: if CI passes, only this synthetic integrity check is reproduced; it is NOT a scientific experiment or proof that historical corpus coverages agree. If real inputs differ, retain fail-closed status and document the mismatch without exposing protected IDs.
