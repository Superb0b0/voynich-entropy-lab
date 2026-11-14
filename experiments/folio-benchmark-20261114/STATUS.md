# VOY-PRED-38 status, 2026-11-14
Status: NON VERIFICATO. This is a benchmark implementation, not a qualifying attempt and not a decipherment.

Hypothesis: a previous-word conditional model predicts words on unseen training-eligible folios better than a global word-frequency model.
Rival: add-half-smoothed unigram; model: add-half-smoothed preceding-word bigram. Split: folio, seeded 20261114, 20% internal test folios from training-only corpus.
Metric: held-out nats/token; exploratory effect = unigram loss minus bigram loss. No hypothesis threshold or generator calibration preregistered, so this run cannot be promoted to a qualified test.
Inputs: only sanitized files provided by VOYNICH_DATA_DIR. The CI workflow checks source corpus hashes against MANIFEST.md and filters protected pages. Never read, list, log, or disclose protected IDs.
Observed: no verified run log, artifact, or result JSON obtained through available GitHub connector; do not claim numerical results. The GitHub connector can fetch file contents but does not expose a general workflow-dispatch/list-runs action. Commit status lookup returned zero statuses; PR-only workflow lookup returned zero PR runs, which is not proof of no push run.
Next action: obtain an actual workflow run/job and artifact, inspect logs and validate parsed P-line counts against independent parser; check for parser markup contamination and correct unknown-word handling before scientific interpretation. Confirm green dedicated workflow and mandatory verify.yml gate before qualifying.
Protected RC1.4.2, RP-01, f085v, anchor staging unchanged.
