# Controllo marginale descrittivo — generatori sintetici
Data 2026-11-15. Non e' una validazione scientifica, non e' l'esperimento 007.

## Metodo
Per ogni generatore, sulle prime parole delle 16667 righe, frequenze di classe `f_k` nell'ordine `qo,ch,sh,d,o,y,s,other`. Per il modello di indipendenza iid, numero atteso su 16666 coppie `E(qoqo)=16666*(f_qo/16667)^2`; `E(same_nonqo)=16666*sum_{k != qo}(f_k/16667)^2`. Si tratta di una baseline teorica che ignora autocorrelazione e non produce p-value.

## Dati e risultati
Fonte blob upstream `karolrybak/voynichese`: Markov SHA-1 Git `4f431843014ecac80728740de7d03ddf19195e75`; volvelle `3ff0c7bd0657238e93e0e46368c35a2547926c58`.
Markov frequenze [2397,2666,1372,1526,3726,840,554,3586].
Volvelle frequenze [2277,2643,1450,1613,3810,755,414,3705].

| Metrica | Markov osservato | Markov atteso iid | O/E | Volvelle osservato | Volvelle atteso iid | O/E |
|---|---:|---:|---:|---:|---:|---:|
| qoqo | 366 | 344.708962 | 1.061765 | 301 | 311.058854 | 0.967663 |
| same_nonqo | 2402 | 2344.228693 | 1.024644 | 2396 | 2440.260610 | 0.981862 |

## Interpretazione
Entrambi i generatori mostrano adiacenze delle classi vicine alle aspettative marginali sotto indipendenza. Questo NON equivale a un test di indipendenza: le righe possono essere autocorrelate e le frequenze non sono stazionarie. Non sono calcolati intervalli o significativita'.
Non e' possibile derivare la corrispondente attesa per il Voynich dai soli `results.json` di 005/006, che contengono conteggi di coppie ma non frequenze di classe per gruppo/paragrafo. Non inventare tali frequenze, ne' stimarle dal totale di `qoqo`. Per un confronto lecito, acquisire le frequenze dal corpus filtrato TRAIN_ONLY e applicare permutazioni all'interno dei paragrafi mantenendo i confini originali. Non aprire HOLDOUT.
Il disegno di campionamento sintetico continuo non e' equivalente ai paragrafi Voynich. Nessuna modifica ai criteri di 005/006 e nessun verdetto 007.
