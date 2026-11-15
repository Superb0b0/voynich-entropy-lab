# SAFE-INPUT-GATE-20261115-0333

Status: BLOCKED_FOR_SCIENTIFIC_EXECUTION; structural safety finding, not a Voynich experiment.

Verified source HEAD: 52412559fd860be1644278881689c6eb70d3e7b7.
main HEAD: 8b81f874a9944e88fe113b19460294a1b1c5a593.
anchor HEAD: ab5871b0950290e76eae127b2e5323b6fc11761b.

## New concrete finding
Read tools/qo_rival_calibration.py on source branch. Its parse() reads the entire original data/ZL3b-n.txt via read_bytes() and subsequently excludes reserved units in Python. It also embeds a literal protected-unit membership set in the source. The claimed training-only analysis therefore has an unsafe data-access boundary for the current no-holdout-access policy. **Do not execute this script** or use its outputs as new scientific evidence. No reserved IDs reproduced in this report.

## Input provenance
MANIFEST.md reports historical corpus SHA256 values, but this cycle did not recompute raw bytes. The GitHub connector read the script and manifest only. No corpus or protected metadata accessed this cycle. Container cannot resolve github.com for a direct byte-level clone.

## Rival next steps
A: run existing qo calibration with post-read exclusion: REJECTED because full corpus is read before filtering.
B: use independently prepared, cryptographically verified, authorized training-only data with no protected membership metadata: SELECTED. Require independent provenance of filtration, no access to original corpus, frozen input SHA256, folio-level split, rival/null and preregistration before any execution.

## Decision
No qualifying scientific attempt, no new p-value, no translation. No change to PROTOCOL.md, HOLDOUT.md, frozen artifacts or historical attempts. Next action: acquire a separately authorized prefiltered training-only corpus, verify its provenance and SHA256 without exposing protected IDs, then preregister a new nonduplicate experiment. Do not rerun qo calibration merely to produce activity.
