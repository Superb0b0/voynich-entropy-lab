# Third-party notices for CAL-01

This notice accompanies the unmodified `cal01-actions-input.zip` (SHA-256: `d962257994bb05d15e0f263d241f6d99fc28d63c4ea67b4f9dea5a6566d43da9`). It is distributed alongside the ZIP, not inserted into it. No scientific input, protocol, or executable is changed by this notice.

## Torsten Timm / Andreas Schinner: self-citation text generator

- Authors of the study: Torsten Timm and Andreas Schinner, *A possible generating algorithm of the Voynich Manuscript* (2019), DOI: https://doi.org/10.1080/01611194.2019.1596999.
- Upstream software: https://github.com/TorstenTimm/SelfCitationTextgenerator
- Pinned upstream reference: `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`, 2019-11-29; https://github.com/TorstenTimm/SelfCitationTextgenerator/tree/a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7
- License at that reference: https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7/LICENSE (Git blob `6b1bd09317974964cf197605719fc6e33a823d94`).
- Historical provenance: archived Round 5 regeneration record identifies the original source ZIP by SHA-256 `dd8db3dceb2d8e1cd3d70e5ce12d8fd9b0a98019c475c067fb10f81adcdbd6f2`. Its main Java source has SHA-256 `7afa236373a997d2e2ccef9a8e7ee799c5766b63ddf161bab8b72ce0f3bbf1e9`, exactly reproduced from the upstream Git blob `62dab4c22f4b4ca631263083789f994789294273`. The upstream source tree, executable tree (including configuration) and MIT license are identical in commits a6ede220, c49e5c4, b1754dd and 98a7f87. The exact commit identity of the historical master ZIP is not independently recovered; the pinned reference identifies the verified matching main source and the stable upstream implementation, not a claimed byte-identical historical ZIP.
- Included materials: `reflow_execution/generator/seed_01.json` through `seed_30.json`, and the corresponding verification manifest. These are locally generated/parsed synthetic outputs, not redistributed Java source, JAR, or upstream archive. The historical regeneration record reports matching text hashes and paragraph sequences for all 30 seeds. The upstream MIT notice is reproduced here in full for attribution; no claim is made that the MIT software license separately defines rights in every possible generated output.

## Upstream MIT license (verbatim)

MIT License

Copyright (c) 2019 Torsten Timm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Voynich transliterations

ZL3b and IT2a: distributed through René Zandbergen's Voynich transliteration resources, https://www.voynich.nu/transcr.html . The source distribution is identified there as CC0. Original authorship/transcriber credits in the corpus headers are retained. The package includes the two original text files, their normalized project JSON derivatives and folio-fold metadata. SHA-256: ZL3b `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; IT2a `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`.

## Other contents

The remaining files are project Python scripts, protocol and manifest documents, checkpoint CSV/JSON, stream checksums, execution log, remote freeze receipt and local audit. Project repository license: MIT, see root LICENSE. No additional third-party corpus, Java source, executable, or compiler is included. Inventory: outer ZIP has driver.py, CAL01_CHECKPOINT_AUDIT.json and a 66-file inner checkpoint ZIP. The inner ZIP contains 2 text corpora, 30 synthetic seed JSONs, 14 other JSONs, 8 Python scripts, 5 checksum files, 4 CSVs, 2 Markdown files and 1 log.
