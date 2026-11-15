# Risultato marginal_null — 2026-11-15
Stato: DESCRIPTIVE_ONLY. Esecuzione CI completata con successo; non e' un test confermativo e non produce un p-value.

## Esecuzione
Workflow: `007 TRAIN_ONLY marginal permutation diagnostic`
Run: https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43739779144
Commit workflow: `2b13ea905437da732b4108afc75382ff4211d41d`
Python 3.11.18. 1.000 permutazioni per corpus, seme 20261115.
La preparazione ha verificato MANIFEST e SHA-256 dei corpus completi, letto HOLDOUT.md solo per identificare le pagine da escludere, prodotto i file filtrati e verificato gli SHA-256 attesi:
- ZL3b training-only: `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9`
- IT2a training-only: `a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c`
Il test negativo `git show HEAD:data/ZL3b-n.txt` e' fallito dopo rimozione di `.git`, come richiesto. Il codice e i dati filtrati sono stati eseguiti da `/tmp/007-sandbox`; nessun `.git` era accessibile da cwd o antenati.

## Metodo
Per ogni corpus, 206 gruppi paragrafo, parole iniziali estratte con la stessa logica di 005/006, e maschera di coppie valide conservata. In ciascuna delle 1.000 repliche, le prime parole sono permutate all'interno di ogni paragrafo; vengono ricalcolati same_nonqo, qoqo e repeat. Questo mantiene le frequenze marginali di parole per paragrafo ma distrugge l'ordine osservato. Intervallo riportato: indici empirici 2,5%-97,5% della distribuzione simulata (25° e 975° valore in ordinamento zero-based, secondo implementazione).
Il test non controlla ancora per trend intra-folio, posizione di riga, colonna, mano, lunghezza della parola o autocorrelazione a livelli diversi dal paragrafo. Il campionamento delle permutazioni e' Monte Carlo.

## Risultati
| Corpus | Coppie valide | Metrica | Osservato | Media nulla | Intervallo 95% |
|---|---:|---|---:|---:|---:|
| ZL3b | 3097 | same_nonqo | 289 | 493.743 | 459–527 |
| ZL3b | 3097 | qoqo | 14 | 64.150 | 52–77 |
| ZL3b | 3097 | repeat | 13 | 23.476 | 15–33 |
| IT2a | 3095 | same_nonqo | 289 | 496.163 | 461–531 |
| IT2a | 3095 | qoqo | 14 | 64.093 | 52–76 |
| IT2a | 3095 | repeat | 12 | 21.797 | 14–32 |

Tutti e sei i conteggi osservati sono sotto il limite inferiore dell'intervallo simulato, con una sola eccezione? No: ZL3b repeat 13 < 15; IT2a repeat 12 < 14. Quindi tutti e sei sono inferiori al limite inferiore. Non si riporta un p-value, poiche' il workflow ha salvato i riassunti e non i 1.000 campioni grezzi.

## Interpretazione limitata
Il semplice rimescolamento delle prime parole entro ciascun paragrafo, pur mantenendo le frequenze di parole di ogni paragrafo, non riproduce i conteggi osservati: le ripetizioni di classe, le sequenze qo-qo e le ripetizioni esatte sono piu' rare nel testo osservato. Il risultato e' coerente con una struttura d'ordine non casuale entro paragrafo.
Non identifica la regola che genera tale struttura, non dimostra che theta+phi sia il modello corretto, non distingue vincoli linguistici, layout, trascrizione o procedura scribale e non decifra il manoscritto. Le trascrizioni ZL3b e IT2a non sono due testi indipendenti.
Non cambia il verdetto 006 (NOT SUPPORTED per il test di sufficienza M2) ne' rende 005/006 confermativi. Richiesti: diagnostiche per strati di posizione/colonna/mano, bootstrap a blocchi o modelli nulli condizionati piu' forti, generatori con struttura comparabile e confronto predittivo preregistrato con calibrazione e correzione multipla.
RC1.4.2 resta CLOSED_PENDING_VALIDATION. Holdout non aperto.
