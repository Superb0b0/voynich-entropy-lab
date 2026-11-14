# CHAR-SHUFFLE-01 — exploratory negative control (2026-11-14)

Status: EXPLORATORY, NOT CI REPRODUCED, NOT VALIDATED. Executed with GitHub-fetched ZL3b-n.txt and IT2a-n.txt. No full-byte SHA256 independently recalculated in this run.

Question: Does within-word letter order carry predictive information beyond character frequencies and word lengths?

Protected holdout: 48 IDs extracted from repository HOLDOUT.md, never logged, excluded from data before analysis. No holdout folio content used. This does not certify the complete holdout policy.

Simplified parser: IVTFF folio header, P-line, [a-z]+ extraction. Eligible folios require >=30 extracted words. 154 eligible ZL3b and 153 IT2a. Fixed pseudo-random folio split (LCG/Fisher-Yates seed 20261114); 30 test folios per corpus. Words prefixed ^^ and suffixed $. Character 0/1/2-history models, additive 0.5 smoothing. Nats per predicted character. Within-word letters shuffled deterministically using seeded Fisher-Yates per word index and folio ID length, preserving word lengths and letter multiset. Same train/test split in original and shuffle conditions. This is a single deterministic shuffle, not a permutation distribution.

| Corpus | Test characters | Original unigram | Original bigram | Original trigram | Shuffled unigram | Shuffled bigram | Shuffled trigram |
| ZL3b | 26936 | 2.6623141707001126 | 1.4919279942921706 | 1.346973950541588 | 2.6623141707001126 | 2.459309479142752 | 2.354029876428352 |
| IT2a | 25177 | 2.6565929656310794 | 1.4172321226484847 | 1.258857538986505 | 2.65659296563108 | 2.416711623466938 | 2.28264529563652 |

Interpretation: a character-order-free within-word shuffle cannot reproduce local sequential predictability. This is an elementary control only. It does NOT rule out structured artificial generators, nor distinguish language from cipher or procedural construction. The parser includes simplified transcription extraction and may incorporate markup. No p-value, uncertainty interval, multi-seed permutation, matched external generator, or independent CI replication. Do not use to claim decipherment.

Frozen RC1.4.2/V7.1 untouched.
