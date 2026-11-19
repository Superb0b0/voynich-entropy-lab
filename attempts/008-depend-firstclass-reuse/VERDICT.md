# Attempt 008 - VOY-DEPEND-01 - verdetto

Verdetto da results.json: **NOT SUPPORTED** (criterio di PROTOCOL.md; calibrazione OK, numerosita' OK). ESPLORATIVO, non qualificante, CI non eseguita -> NON VERIFICATO fino al job verde.

Sequenza: protocollo e codice scritti prima di vedere qualsiasi output; un solo run sui dati reali (nessuna correzione del codice dopo); l'analisi di potenza piantata qui sotto e' successiva al verdetto e descrittiva.

## Analisi primaria (coppie interne, nullo a estremi fissi, strati per lunghezza)

| split | coppie | X=1 | media Y (X=0) | S_adj | effetto relativo | p (2 code) | stesso segno senza un folio |
|---|---|---|---|---|---|---|---|
| 0 | 1613 | 155 | 0.066827 | -0.00858 | -0.128386 | 0.2185 | 1.0 |
| 1 | 1060 | 118 | 0.061966 | 0.004128 | 0.06661 | 0.6145 | 1.0 |

Segni opposti nei due split e nessun p vicino a 0,025: nessuna evidenza che la ripetizione della classe iniziale modifichi il riuso del corpo.

## Calibrazione (richiesta dal protocollo)
- split 0: dimensione 0.05 (soglia <= 0,07), potenza su effetto piantato 1.0 (soglia >= 0,60)
- split 1: dimensione 0.0 (soglia <= 0,07), potenza su effetto piantato 1.0 (soglia >= 0,60)

## Potenza per effetti piu' piccoli (POST HOC, descrittiva, 40 simulazioni)
Effetto piantato = probabilita' q di sostituire un token del corpo con uno della riga precedente nelle coppie X=1; S_adj medio piantato include la base osservata (-0,0086 split 0, +0,0041 split 1).
| split | q | S_adj medio piantato | potenza (p<=0,025) |
|---|---|---|---|
| 0 | 0,05 | -0,0019 | 0,00 |
| 0 | 0,10 | +0,0048 | 0,00 |
| 0 | 0,25 | +0,0280 | 0,975 |
| 1 | 0,05 | +0,0117 | 0,00 |
| 1 | 0,10 | +0,0181 | 0,375 |
| 1 | 0,25 | +0,0369 | 1,00 |

Lettura: il test rileva con affidabilita' un aumento di S_adj di circa +0,03-0,04 (circa +45-60% del riuso di base) e non rileva aumenti di circa +0,01-0,02. NOT SUPPORTED significa quindi "nessuna dipendenza grande", non "nessuna dipendenza".

## Descrittivi (nessun peso sul verdetto)
- Con estremi inclusi e con parser B i segni e gli ordini di grandezza restano quelli della primaria (p fra 0,29 e 0,59).
- Coppie qo->qo interne: 12 (split 0) e 2 (split 1): nessuna inferenza possibile.

## Cosa cambia
Su questi dati la ripetizione della classe iniziale e il riuso del corpo non risultano collegati in modo rilevabile. Resta compatibile con due fenomeni indipendenti; non esclude un legame di dimensione modesta. Il riuso fra righe e' stato gia' misurato sul corpus completo: nessun risultato qui e' una scoperta indipendente.
