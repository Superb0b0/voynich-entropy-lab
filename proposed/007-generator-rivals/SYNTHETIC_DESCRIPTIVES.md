# Benchmark lineare — primi descrittivi dei corpus sintetici
Data: 2026-11-15. Stato: DESCRIPTIVE_ONLY, non inferenza Voynich, non risultato dell'esperimento 007.

## Provenienza
Repository upstream: https://github.com/karolrybak/voynichese
I contenuti sono stati letti direttamente con GitHub fetch_blob identificati da SHA-1 Git:
- Markov: `4f431843014ecac80728740de7d03ddf19195e75`
- Volvelle: `3ff0c7bd0657238e93e0e46368c35a2547926c58`
Questi identificativi verificano l'oggetto Git richiesto; non costituiscono SHA-256 indipendente sui byte. Nessuna attestazione di filtraggio o isolamento dell'holdout.

## Metodo eseguito
Dividere il testo in righe dopo rimozione del newline finale. Per ogni riga prendere la prima parola separata da whitespace, lowercase, rimuovere caratteri non a-z. Classe: primo prefisso corrispondente nell'ordine `qo,ch,sh,d,o,y,s`; altrimenti `other`. Contare ogni coppia di righe adiacenti nel file, senza inventare paragrafi o folii. `same_nonqo` quando le classi coincidono e non sono qo; `qoqo` quando entrambe qo; `repeat` quando le prime parole coincidono esattamente.

| Metrica | Markov | Volvelle |
|---|---:|---:|
| righe valide | 16667 | 16667 |
| coppie | 16666 | 16666 |
| same_nonqo | 2402 (0.1441257650) | 2396 (0.1437657506) |
| qoqo | 366 (0.0219608784) | 301 (0.0180607224) |
| repeat | 120 (0.0072002880) | 4 (0.0002400096) |

Distribuzione classi delle prime parole, ordine `qo,ch,sh,d,o,y,s,other`:
- Markov: [2397,2666,1372,1526,3726,840,554,3586]
- Volvelle: [2277,2643,1450,1613,3810,755,414,3705]

## Riproducibilita'
Il seguente pseudocodice e' sufficiente a ricalcolare i conteggi dai blob testuali upstream: `lines=text.rstrip("\\n").split("\\n"); words=[re.sub("[^a-z]","",line.split()[0].lower()) for line in lines]; classes=[next((i for i,p in enumerate(("qo","ch","sh","d","o","y","s")) if w.startswith(p)),7) for w in words]; for each consecutive pair count same_nonqo, qoqo and repeat as defined above`.
Nessuna statistica di significativita' o intervallo e' stata calcolata; nessun campionamento e nessuna correzione multipla.

## Interpretazione limitata
Il Markov presenta 120 ripetizioni esatte contro 4 del volvelle (rapporto 30:1 sui conteggi), mentre `same_nonqo` ha proporzioni simili. La differenza non prova nulla sulla genesi del manoscritto senza un confronto prespecificato su unita' e dati comparabili, controllo delle frequenze marginali e audit di contaminazione.

Stato 007: NOT_RUN. Stato RC1.4.2: CLOSED_PENDING_VALIDATION. Non e' stato letto alcun testo holdout.
