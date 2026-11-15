# Position-stratified null — preregistrazione v0.1
Data: 2026-11-15. Stato: FROZEN_BEFORE_RUN. Nessun risultato osservato al momento della registrazione.

## Domanda
La soppressione di adiacenze same_nonqo, qoqo e repeat resta presente quando, oltre alle frequenze per paragrafo, si conserva anche la distribuzione delle prime parole fra posizioni iniziali, centrali e finali di ciascun paragrafo?

## Popolazione e protezione
Solo ZL3b-n.txt e IT2a-n.txt TRAIN_ONLY, prodotti dal verificatore esistente e confrontati con gli SHA-256 filtrati congelati:
- ZL3b: dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9
- IT2a: a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c
Nessuna lettura del contenuto HOLDOUT; il file HOLDOUT.md può essere usato soltanto dal verificatore per escludere pagine protette. Esecuzione da sandbox senza .git, con test negativo git show.

## Null condizionato
Replicare la tokenizzazione e la costruzione dei gruppi di marginal_null.py. Per ogni paragrafo con n righe P valide per tokenizzazione, assegnare ogni posizione i alla terzina di posizione:
- early se 3*i < n
- middle se n <= 3*i < 2*n
- late se 3*i >= 2*n
Equivalentemente bucket(i)=min(2, floor(3*i/n)).
A ogni replica, permutare uniformemente le prime parole SOLO fra posizioni dello stesso bucket e dello stesso paragrafo. Non spostare parole fra paragrafi. Conservare la maschera delle coppie di numeri di riga consecutivi definita dal parser originale. Il testo osservato non viene permutato.
Calcolare gli stessi conteggi: same_nonqo, qoqo, repeat.

## Parametri congelati
1.000 repliche per corpus; random.Random(20261116); ordine corpus ZL3b poi IT2a. Riportare osservato, media nulla, intervallo empirico 95% agli indici ordinati [24] e [974], min/max, conteggio coppie e gruppi. Nessun p-value post-hoc; nessuna modifica di seed/repliche dopo aver visto risultati.

## Regola di lettura
Questo null conserva distribuzione delle parole per paragrafo e per terzina di posizione, ma non conserva posizione esatta, dipendenze di colonna, mano, folio, lunghezza, né struttura lessicale. Se gli osservati sono sotto l'intervallo, il null coarse-position non li spiega; non significa che la regola sia linguistica o che il manoscritto sia decifrato. Se gli osservati rientrano, il precedente effetto può essere in parte spiegato da distribuzioni posizionali. Entrambi gli esiti sono informativi.
Nessuna promozione di 005/006 o modifica RC1.4.2. Questa è una diagnostica esplorativa preregistrata, non un attempt qualificante secondo PROTOCOL.md.
