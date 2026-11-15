# Risultato position-stratified null — 2026-11-15
Stato: DESCRIPTIVE_ONLY. Workflow CI verde; diagnostica preregistrata, non attempt qualificante.

## Esecuzione
Workflow: https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43740724249
Commit workflow: `79c4dd99ead8cc10099d4b34a420eb641b1ca02e`
Python 3.11, 1.000 repliche per corpus, seed 20261116.
Verificati hash del corpus completo contro MANIFEST, filtraggio TRAIN_ONLY tramite verifier, hash filtrati congelati e test negativo `git show` dopo rimozione di `.git`. Nessun contenuto holdout aperto.

## Metodo
Null congelato in POSITION_STRATIFIED_NULL_SPEC.md. In ciascun paragrafo le prime parole sono permutate solo tra posizioni appartenenti alla stessa terzina (early/middle/late), preservando la distribuzione lessicale per paragrafo e per terzina. Si conserva la maschera delle coppie di righe numericamente consecutive. Statistiche: same_nonqo, qoqo, repeat. Intervallo empirico [24], [974] delle 1.000 repliche.

## Risultati
| Corpus | Coppie | Metrica | Osservato | Media nulla | Intervallo 95% |
|---|---:|---|---:|---:|---:|
| ZL3b | 3097 | same_nonqo | 289 | 449.234 | 419–480 |
| ZL3b | 3097 | qoqo | 14 | 54.668 | 44–65 |
| ZL3b | 3097 | repeat | 13 | 19.805 | 12–28 |
| IT2a | 3095 | same_nonqo | 289 | 450.952 | 422–484 |
| IT2a | 3095 | qoqo | 14 | 54.261 | 43–65 |
| IT2a | 3095 | repeat | 12 | 18.631 | 11–27 |

## Lettura
Il controllo posizionale riduce le medie nulle rispetto al rimescolamento libero entro paragrafo, ma non spiega la soppressione di adiacenze di classe: in entrambe le trascrizioni, same_nonqo e qoqo osservati restano sotto il limite inferiore. La ripetizione esatta, invece, rientra nell'intervallo in entrambe le trascrizioni. Quindi il risultato precedente sulla ripetizione esatta NON resiste a questo controllo più forte.
La proprietà che sopravvive e' la riduzione di adiacenze same_nonqo e qo-qo rispetto a un null che conserva le frequenze per paragrafo e per terzina di posizione. Non prova ancora un meccanismo specifico: rimangono confondenti di posizione esatta, colonna, mano, folio, lunghezza, contesto lessicale e struttura di trascrizione. ZL3b e IT2a non sono corpora indipendenti.
Nessun p-value; gli intervalli sono descrittivi Monte Carlo. Non dimostra semantica, lingua o decifrazione. Prossimo controllo: stratificazione per coordinate/colonna IVTFF e per mano, se codificate in modo affidabile; quindi null per posizione esatta/regioni locali e confronto predittivo preregistrato.
RC1.4.2 resta CLOSED_PENDING_VALIDATION.
