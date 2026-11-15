# Benchmark separato sulle righe — specifica preregistrata v0.1
Data 2026-11-15. STATO: SPEC_ONLY; nessuna analisi statistica eseguita, nessun risultato.

## Fonti osservate
I blob pubblici `karolrybak/voynichese` sono stati letti direttamente tramite GitHub fetch_blob:
- Markov SHA-1 Git `4f431843014ecac80728740de7d03ddf19195e75`, 1.215.853 caratteri, 16.667 righe di testo (16.668 segmenti split con newline finale), zero righe vuote, nessun marcatore IVTFF.
- Volvelle SHA-1 Git `3ff0c7bd0657238e93e0e46368c35a2547926c58`, 1.212.530 caratteri, 16.667 righe di testo, zero righe vuote, nessun marcatore IVTFF.
I numeri sono derivati dal testo restituito dal connettore, NON da SHA-256 dei byte; il blob SHA-1 Git non e' un attestato di filtraggio.
Il README upstream dichiara 200.000 parole sintetiche per corpus, con Markov di caratteri ordine 3 + 15% self-citation e volvelle a tre anelli indipendenti. Questi output NON preservano i paragrafi del Voynich.

## Ipotesi testabile distinta da 005/006
Su sequenze di prime parole di righe consecutive, i corpus generati differiscono dal Voynich TRAIN_ONLY per l'adiacenza di classi di prefisso, dopo controllo per frequenze delle classi e struttura delle sequenze. Non e' una prova di semantica o di decifrazione.

## Unita' e statistica (congelate)
Tokenizzazione di ogni riga sintetica: split whitespace; prima parola convertita a lowercase e ripulita di caratteri non a-z; escludere riga se non resta alcuna parola.
Classi ordinate: qo, ch, sh, d, o, y, s, other (come 005).
Statistiche su coppie di righe consecutive all'interno della stessa sequenza: `same_nonqo`, `qoqo`, `repeat` (stessa prima parola).
Il confronto primario usa le proporzioni per coppia valida, non i conteggi grezzi. Non inventare confini di paragrafo nei sintetici.

## Unita' sintetiche e controllo
L'unita' sintetica e' l'intero file continuo. Per bootstrap/blocchi e autocorrelazione si deve preregistrare la dimensione dei blocchi e la strategia di campionamento prima dell'analisi; non usare lo split per folio dei test 005/006. Il confronto col Voynich richiede un estrattore che utilizzi esclusivamente il corpus filtrato TRAIN_ONLY e che mantenga le vere adiacenze all'interno di paragrafi, distinguendo chiaramente il diverso disegno campionario.
Non confrontare numeri grezzi di righe sintetiche con le 3097/3095 coppie valide dei test 005/006 come se le strutture fossero identiche.

## Stop obbligatori
Prima di qualunque inferenza: (1) SHA-256 su byte acquisiti e commit upstream fissato; (2) licenze e provenienza; (3) audit che dimostri assenza di contaminazione dei generatori con i folii HOLDOUT; (4) ambiente senza .git e test negativo git show; (5) piano di campionamento per blocchi, numero simulazioni, seed, correzione multipla, criteri numerici di fallimento preregistrati; (6) calibrazione con generatori a verita' nota.
In mancanza di una condizione: NOT_RUN. Il benchmark e' separato e non cambia i verdetti 005/006. RC1.4.2 rimane CLOSED_PENDING_VALIDATION.
