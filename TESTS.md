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


## Aggiornamento audit 2026-11-15: gate storico e conferma indipendente

- **001: PROVENIENZA STORICA VERIFICATA**, tramite workflow `Historical attempt 001 provenance (no corpus)`, run [43736785320](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43736785320), conclusione **SUCCESS**. Sono stati confrontati file originali, impronta del programma e manifesto con il commit sorgente `0e87d9758f288cdeac29513ee04245dcd8126592`. Questo controllo non apre corpus o holdout e **non è una riproduzione del risultato**.
- **001: RIPRODUCIBILITÀ NON VERIFICATA**. Il programma storico richiede esplicitamente SHA-256 e numero di record del corpus integrale, incompatibili con il corpus training-only filtrato. Non introdurre un contratto `attempt.yml` fittizio o modificare i risultati archiviati.
- **CI generale: FAIL**, run [43736785321](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43736785321), errore `001-paragraph-header-key: missing attempt.yml; cannot infer execution contract`. Test isolati [43736785325](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43736785325): **SUCCESS**. Il successo isolato non sostituisce la CI generale.
- **002–004: NON VERIFICATI** dalla CI generale; il verificatore si interrompe a 001, quindi non si possono attribuire loro esiti di replay sulla base di questa esecuzione.
- **ANCHOR-02 qo: LOCKED_PENDING_GATE**. Autorizzazione dell'utente all'eventuale apertura controllata acquisita il 2026-11-15, **subordinata** ai gate già preregistrati. Nessun campione protetto aperto; nessuna conferma indipendente dichiarabile.
- **Decisione metodologica**: mantenere separati audit di provenienza storica e nuovo replay training-only. Un nuovo esperimento su dati filtrati deve avere nuovo ID, protocollo e risultati propri, senza retroattribuire la riproduzione al tentativo 001.
