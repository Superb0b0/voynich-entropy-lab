# Attempt 007: confronto falsificabile con generatori rivali (PREREGISTRATION ONLY)
Data di registrazione: 2026-11-15.
Stato: DESIGN_FROZEN_PENDING_INPUTS. Nessun esperimento eseguito; nessun risultato, p-value o verdetto scientifico.

## Domanda
Il modello a due parametri (theta, phi) di 005/006 predice i tre conteggi di adiacenza su folii di addestramento meglio di generatori indipendenti, senza sfruttare differenze di impaginazione, lunghezza delle righe o trascrizione?

## Vincoli e provenienza
- Corpus originali immutati: ZL3b SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc; IT2a SHA-256 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5.
- Solo dati TRAIN_ONLY filtrati dal verificatore; vietati HOLDOUT.md come input del tentativo e testo dei folii riservati. Nessuna lettura diretta dei corpus originali durante l'esecuzione dell'attempt.
- Riutilizzare classi, split per folio, statistiche, seme e procedura predittiva di 005/006, senza ritocchi dopo osservazione dei risultati. Mantenere i due esiti storici come baseline, incluso il fallimento 006.
- Generator inputs: acquisire output pubblici Timm-Schinner e almeno un generatore di controllo noto, con licenza/provenienza, versione, URL/commit, SHA-256 e attestazione indipendente del processo di filtraggio. Non considerare disponibili i dati finche' questi elementi non sono verificati. Nessun generatore sostitutivo inventato.
- Predefinire per ciascun generatore il mapping delle righe e dei paragrafi; se non puo' preservare le unita' necessarie, escluderlo con motivazione prima di calcolare le statistiche.
- Calibrazione preliminare su dati sintetici con verita' nota, separati dal corpus Voynich: controllo positivo (theta e phi noti) e negativo (theta=phi=0); documentare bias, copertura intervalli e diagnostiche MCMC. Una calibrazione fallita blocca l'analisi Voynich.
- Confronto a parita' di struttura: stessi conteggi di righe per paragrafo, stesse adiacenze valide, stessa dimensione campionaria, stesso numero di simulazioni e stessi criteri per tutti i rivali.
- Confondenti: lunghezza della prima parola, trascrizione ZL3b/IT2a, distribuzione dei prefissi e layout. Analisi di sensibilita' prespecificate, senza selezione del risultato migliore.

## Criteri di arresto (prima dei risultati)
FAIL_CLOSED se manca uno qualsiasi di: generatori verificabili, hash input, filtraggio indipendente attestato, mapping valido, calibrazione positiva e negativa, diagnostica di convergenza, CI che impedisca accesso a .git e agli input protetti. Non produrre un verdetto scientifico in quel caso.

Per ciascuna delle tre statistiche (same_nonqo, qoqo, repeat) e per ciascuna delle due direzioni di split, riportare osservato, distribuzione predittiva e intervallo 95% per M2 e per ogni rivale. Il criterio storico 005/006 rimane immutato: M2 deve contenere tutte e sei le osservazioni, M1 deve escludere qoqo in entrambe le direzioni. Un vantaggio sui generatori esterni richiede, in aggiunta, una metrica di scoring predittivo preregistrata e un confronto corretto per test multipli: NON eseguire quel confronto prima di fissare numericamente metrica, soglia, numero di rivali e correzione in un addendum datato e congelato. Questo documento NON afferma superiorita' a nessun rivale.

## Condizioni tecniche
Il replay CI 005/006 e' verde nel workflow dedicato, ma verify.yml generale fallisce su 001 senza attempt.yml. Il controllo strace attuale non blocca il percorso git show HEAD:data/...; eseguire il nuovo attempt solo in ambiente senza directory .git e con test negativo che dimostri il blocco del bypass, senza alterare i risultati originali o il verificatore storico durante l'archiviazione.

## Prossimo gate
Acquisire e verificare gli output dei generatori e la relativa attestazione indipendente; congelare l'addendum di scoring; poi implementare il codice ed eseguire la calibrazione. Nessun accesso all'holdout. RC1.4.2 resta CLOSED_PENDING_VALIDATION.
