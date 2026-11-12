# Voynich ANCHOR · isolated rev3 staging

**Status: DRAFT / EXPLORATORY / NOT SCIENTIFICALLY VALIDATED / NOT FROZEN.**

This directory preserves an ANCHOR revision 3 kit recovered from the user's ChatGPT Library on 2026-11-12.

## Recovered and copied byte-for-byte

The seven extracted text files from `Voynich_ANCHOR_rev3.zip` are under [original-extracted](original-extracted/):

- `README.md`
- `REV2_SHA256.txt`
- `SHA256SUMS`
- `anchor_entry.schema.json`
- `requirements.txt`
- `tests/test_anchor_schema.py`
- `validate_anchor.py`

The Git blob IDs of these GitHub files were compared with the corresponding original ZIP entry bytes (including newlines and UTF-8 content). All seven matched.

Original source ZIP SHA-256: `0ed5f5f234c6b0b5acdbbb8e5ddf5d76a86bc94c427f31b2924a49a05ba0064f`.

Original revision 2 ZIP SHA-256: `9d0ffceec94c641639024255ee280b68b493c4364541f6ede56ce90dc8accb06`.

The rev2 `anchor_entry.schema.json` original SHA-256 matches `fdff56233ee75bc7330a82b50562cb8829af60dbaf2fe181498f920d7fa425b1`, as declared in `REV2_SHA256.txt`.

`imported-entry/ANC-0001.json` was also copied byte-for-byte from `ANCHOR02_import_rev3.zip`, which has SHA-256 `6a3d010de22d5b1a45f5d793170383cfcd8767bc190e4143a796d1b0d62c3bee`.

## Tests

On the recovered original ZIP, `python tests/test_anchor_schema.py` returned **TOTAL 59 ANOMALIE 0** (12 November 2026). The alternate command `python -m pytest -q` failed at collection because the script's `test(name,mod,expected)` helper is interpreted as a pytest test requiring fixtures. This is not an indication of a failing native 59-case suite.

No independent reviewer approval, byte-level verification of evidence references, or frozen scientific status is implied.

## Separate, non-canonical Library extracts

`../library-import/text/` contains text **re-rendered** by the Library's text reader. Some copies may differ in byte count, line endings, or text formatting. They are for consultation, **not** replacements for the original files and **not** valid for matching historical SHA-256 receipts.

`../library-inventory/VOYNICH_LIBRARY_INDEX_20261112.json` catalogs the discoverable project files; the vast majority are **not uploaded**. In particular, ZIPs, images and other binary materials remain in the Library; the original ZIPs are not part of this GitHub branch.

## Safety boundaries

- Nothing was written to `main`.
- Rev2 and any frozen RC1.4.2/V7.1 material remain unchanged.
- `RC1.4.2` stays `CLOSED_PENDING_VALIDATION`; `f085v` remains unresolved; `RP-01` remains open.
- This revision is an evidence-entry schema draft, not a decoding claim or a validation of geometric/semantic hypotheses.
