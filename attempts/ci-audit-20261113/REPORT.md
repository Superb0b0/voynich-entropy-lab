# CI-AUDIT-20261113: scheduled workflow discrepancy
Status: STATIC AUDIT ONLY. No workflow run claimed.

## Evidence
On main, `.github/workflows/autonomous-voynich.yml` Git blob `36847cb509a04a80b951008852d0be68e3889b43` contains a literal backslash-n after `run: python tools/qo_rival_calibration.py`, immediately before the archive step: `run: python tools/qo_rival_calibration.py\\n      - name: Archive results...`. This is not a YAML line break. The intended separate `- name: Archive` step is therefore not represented as an ordinary YAML step in that text. The scheduled workflow may fail YAML parsing or shell execution; actual Actions status not established.

On research/voy-cal01-synthetic-20261113, the same workflow has blob `ed03ba85a711f23fc93482d828505db2c3e4f245` and **omits** the calibration step entirely. Thus this branch is not a safe direct replacement for main.

## Minimal proposed main fix (NOT APPLIED)
Replace the literal `\\n` with an actual newline, keeping the calibration command and the archive step on distinct YAML lines. Fetch main blob again immediately before an authorized update; use its expected content SHA and never force push. Verify workflow parsing and real GitHub Actions logs after change.

## Scientific implications
Scheduled runs cannot be treated as evidence of qo calibration without verified execution logs and artifact hashes. The synthetic CAL-01 CI is a separate workflow and is not evidence of ms408/Naibbe/Timm–Schinner validation. No Voynich text or holdout read in this audit.

Next: reconcile main workflow safely, validate Actions execution, then audit training-only rival generator provenance and parser equivalence.
