# TESTS.md - registro dei test (creato 2026-11-13)

Conservare protocolli e verdetti inalterati. La definizione di tentativo QUALIFICANTE stabilita nel successivo PROTOCOL.md v1 è più severa dei test esplorativi già svolti; non retro-promuovere.

**Stato CI al 2026-11-13:** **NON VERIFICATO** per tutti i tentativi registrati (001–004): non è stata accertata alcuna esecuzione verde di `.github/workflows/verify.yml` sul commit pertinente. I valori storici qui sotto restano descrittivi e non sono risultati verificati dalla CI. Una CI verde futura non equivale da sola a validazione scientifica.

| ID | Ipotesi / famiglia | Esito | P non corrette | Stato rispetto a PROTOCOL.md v1 |
|---|---|---|---|---|
| 001 | Apertura del paragrafo come chiave lessicale a distanza; 2 split indipendenti per folio | non sostenuta | 0,746; 0,002 | NON QUALIFICANTE: manca calibrazione su generatori noti e completo controllo dei confondenti |
| 002 | Interazione Currier A/B sulla differenza di overlap; 2 split indipendenti per folio | non sostenuta | 0,539; 0,131 | NON QUALIFICANTE: manca calibrazione su generatori noti e completo controllo dei confondenti |

A fini descrittivi, Holm per i due p dello 001 produce 0,746 e 0,004 rispettivamente; Holm per il 002 produce 0,539 e 0,262 rispettivamente. Questa correzione non altera il verdetto: il successo richiedeva entrambi gli split, non uno solo. Nessun risultato è VALIDATO o tradotto.

Input principali: ZL3b-n.txt (bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc), parser RC1.2 (8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5).

| 003 | First-word exact-repeat avoidance, training only, 2 folio splits, within-paragraph shuffled rival | NOT SUPPORTED | 0.017982; 0.177822 | EXPLORATORY; Holm across 2 splits 0.035964; 0.177822, not family-wide |
| 004 | qo->qo first-word transition depletion, training only, 2 folio splits, within-paragraph shuffled rival | TRAINING SIGNAL, not independently confirmed | 0.000999; 0.000999 | EXPLORATORY; Holm across 2 splits 0.001998 each, not family-wide; prior whole-corpus leakage |

## Engineering replay 005 (2026-11-14)

`005-train-isolation-smoke` is **NOT A SCIENTIFIC ATTEMPT**. It only checks the filtered training input hash, bytes, lines and instrumented read isolation. Its successful CI run, if any, must not change the **NON VERIFICATO** status of scientific attempts 001–004, and must not be counted as a qualifying scientific experiment. The archived evidence in 001–004 is unchanged. See `research/audit-remediation-20261114.md`.
