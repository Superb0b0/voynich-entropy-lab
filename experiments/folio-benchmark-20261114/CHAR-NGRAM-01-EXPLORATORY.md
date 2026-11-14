# CHAR-NGRAM-01 — exploratory executed comparison (2026-11-14)

Status: EXPLORATORY / NOT CI-REPRODUCED / NOT SCIENTIFICALLY VALIDATED.

Source: GitHub repository Superb0b0/voynich-entropy-lab main, data/ZL3b-n.txt and data/IT2a-n.txt, retrieved through GitHub connector. Historical corpus SHA-256 expected: ZL3b bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc; IT2a 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5. These full SHA-256 digests were NOT independently recalculated in this run.

Privacy/holdout: protected page IDs extracted from HOLDOUT.md in memory, not printed, and excluded before model construction or evaluation. 48 protected IDs matched the extractor; their identifiers and content were not logged. This does not independently certify the holdout policy.

Parser: IVTFF page headers /^<(f\\d+[rv]\\d*)>\\s+<!/ and paragraph lines /^<f\\d+[rv]\\d*\\.[^>]*[,@+]P\\d*>/. Text after first > and before <!; lowercase contiguous [a-z]+ words; folios with >=3 qualifying lines. WARNING: this simplified extraction can retain transcription markup letters and does not implement full IVTFF canonical parsing.

Split: 160 eligible folios per transcription, 128 training, 32 test. Sorted folio IDs, Fisher-Yates shuffle using unsigned LCG seed 20261114 (state = 1664525*state + 1013904223 modulo 2^32). Same test split for both transcriptions. No held-out folio training.

Models: character unigrams, bigrams and trigrams (0,1,2 previous characters) within each word; prefix ^^ and suffix $; additive 0.5 smoothing; alphabet size = observed training character types + 1. Predict positions i>=2 in ^^word$ including end marker. Log-loss in natural logarithm nats per predicted character.

Results:
| transcription | test characters | unigram | bigram | trigram | gain trigram vs bigram | folios trigram beats bigram |
| ZL3b | 24529 | 2.652502606918201 | 1.4384110344355288 | 1.2942984559891306 | 0.14411257844639805 | 32/32 |
| IT2a | 23807 | 2.659260599660927 | 1.4131237163174994 | 1.2540081972489223 | 0.1591155190685773 | 32/32 |

Interpretation: strong out-of-folio character-local predictability. This does not distinguish natural language, cipher, or generative text. No calibrated known-generator rival, uncertainty interval, full parser verification, CI reproduction, or independent second implementation. This is not decipherment.

No changes to frozen RC1.4.2/V7.1 assets. No builder, PCA, clustering, or conditional coupling executed.
