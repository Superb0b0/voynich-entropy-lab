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


## Audit correttivo QO — 2026-11-15 (append-only; prevale sui riepiloghi informali)

La correzione versionata in `research/qo-rival-03-page-collision-correction.md` (commit `b19d701fcffe931ead9769defc0b4b0b252ec5f3`) documenta una collisione recto/verso nelle precedenti analisi QO-RIVAL-01/02: raggruppare per numero di foglio anziché per identificativo completo della pagina poteva fondere pagine diverse. Le cifre precedenti 28/272, 115 gruppi e 59/59 leave-one-folio-out sono formalmente ritirate e non vanno citate come risultati affidabili.

La correzione riporta un'analisi esplorativa distinta su gruppi pagina-paragrafo: 14/396 transizioni qo→qo, 211 gruppi; null shuffle entro paragrafo e entro foglio, 2.000 permutazioni, seed 20261113, p Monte Carlo 0,00049975 per ciascun nullo (Holm 0,00099950). Anche questi numeri restano **ESPLORATIVI**, perché la correzione è post-hoc, il parser non è ancora riconciliato con RC1.x e i nulli sono shuffle semplici, non generatori testuali completi. Non costituiscono conferma indipendente o interpretazione semantica.

Il tentativo 004 in `attempts/004-qo-transition/` riporta separatamente un segnale training-only (12/263 e 2/133; p Monte Carlo 0,000999 per split), ma il suo stesso verdetto lo classifica ESPLORATIVO: la pista qo era già stata osservata sull'intero corpus prima della selezione dei folii training. Di conseguenza, i folii interni non possono essere ri-etichettati come conferma indipendente della medesima ipotesi. Non aprire il campione protetto per una conferma retroattiva: il leakage di selezione non si annulla con un'autorizzazione successiva.

**Decisione:** sospendere ogni claim confermativo su qo. Prima di un nuovo test servono parser canonico validato contro RC1.x, unità pagina/folio definite senza collisioni, ipotesi nuova non selezionata guardando il campione, generatori rivali appropriati e preregistrazione antecedente. L'autorizzazione dell'utente all'apertura del campione non supera questi vincoli metodologici. Nessun holdout aperto in questo audit.
