# Confronto descrittivo preliminare: Voynich training vs sintetici
Data 2026-11-15. Stato: EXPLORATORY_DESCRIPTIVE_ONLY. Non e' il test 007; nessun p-value o conclusione causale.

## Provenienza dei numeri Voynich
Dati letti direttamente da `attempts/005-refractory-qo-parameter/results.json` e `attempts/006-it2a-replication/results.json` sul ramo `attempts-005-006` di `Superb0b0/voynich-entropy-lab`.
ZL3b (005): split 0=1871 coppie, split 1=1226, totale 3097. Conteggi osservati (da `observed_fit` nei due split): same_nonqo 163+126=289; qoqo 12+2=14; repeat 6+7=13.
IT2a (006): split 0=1871, split 1=1224, totale 3095. same_nonqo 161+128=289; qoqo 12+2=14; repeat 7+5=12.
I valori `data_sha256` nei risultati riguardano i corpus filtrati di training, non gli originali completi.
Entrambi i risultati sono esplorativi. 005=SUPPORTED nel criterio interno; 006=NOT SUPPORTED. CI dedicata di replay 005/006 verde; verifier globale non verde per assenza di attempt.yml in 001.

## Provenienza sintetici
Conteggi ricavati direttamente dai blob upstream `karolrybak/voynichese` (Markov SHA-1 `4f431843014ecac80728740de7d03ddf19195e75`; volvelle SHA-1 `3ff0c7bd0657238e93e0e46368c35a2547926c58`). Per ogni sintetico 16667 righe, 16666 coppie continue.
Non e' stato attestato filtraggio di training indipendente, ne' calcolato SHA-256 sui byte originali.

## Tabella
| Corpus | coppie | same_nonqo | qoqo | repeat |
|---|---:|---:|---:|---:|
| Voynich ZL3b training | 3097 | 289 (9.331611%) | 14 (0.452050%) | 13 (0.419761%) |
| Voynich IT2a training | 3095 | 289 (9.337641%) | 14 (0.452342%) | 12 (0.387722%) |
| Markov sintetico | 16666 | 2402 (14.412577%) | 366 (2.196088%) | 120 (0.720029%) |
| Volvelle sintetico | 16666 | 2396 (14.376575%) | 301 (1.806072%) | 4 (0.024001%) |

## Interpretazione e limiti
Le proporzioni `qoqo` sintetiche sono circa 4.86 (Markov) e 4.00 (volvelle) volte quella di ZL3b; questo rapporto non controlla per frequenze marginali, struttura dei paragrafi, autocorrelazione, selezione dei confini, lunghezza di riga, trascrizione o contaminazione. Non si puo' inferire superiorita' del modello theta+phi.
La ripetizione esatta e' inferiore nel volvelle ma superiore nel Markov rispetto al training Voynich, e le due metriche di classe non- qo dei sintetici sono superiori.
I test 005/006 misurano soltanto coppie consecutive valide all'interno dei paragrafi, mentre i sintetici usano ogni coppia continua. Le popolazioni e il disegno campionario NON sono equivalenti. Non usare questa tabella per p-value, intervalli o verdetto preregistrato.

## Prossima azione
Verificare frequenze marginali delle classi sul training Voynich senza accesso all'holdout, e stabilire un disegno comune di campionamento/stratificazione prima di qualsiasi inferenza. Audit del filtraggio dei generatori e ambiente CI senza .git restano obbligatori.
RC1.4.2: CLOSED_PENDING_VALIDATION.
