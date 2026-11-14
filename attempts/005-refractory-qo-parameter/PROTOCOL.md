# Attempt 005 - modello refrattario di classe con parametro specifico per qo (ZL3b)
Data: 2026-11-14. Stato: ESPLORATIVO.

## Dati e confini
- Corpus completo (atteso, da MANIFEST.md): bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc. Lo script NON lo apre: legge solo $VOYNICH_DATA_DIR/ZL3b-n.txt, la versione filtrata training-only prodotta da tools/verify_attempts.py (stessa logica: rimozione dei blocchi pagina riservati da HOLDOUT.md). SHA-256 della versione filtrata usata in locale: dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9.
- Holdout non aperto. Per costruire il filtro sono stati letti solo gli ID di pagina di HOLDOUT.md, non il testo dei folii riservati.
- Parser: stessa estrazione semplificata della prima parola di 003/004 (righe P, rimozione di <...>, {...}, [...]; separatori punto, virgola, spazio; minuscole a-z); NON e' il parser RC1.2 certificato.
- Unita': paragrafo (*P/@P apre un nuovo paragrafo), righe numerate consecutive; split per folio con SHA256(foglio+':20261114') pari/dispari, come 003/004.

## Modello (fissato prima dell'esecuzione finale)
Classi della prima parola per prefisso, in ordine: qo, ch, sh, d, o, y, s, altro. Dentro ogni paragrafo l'ordine delle prime parole ha probabilita' proporzionale a exp(-E), con E = somma, sulle coppie consecutive di righe consecutive di stessa classe, del peso theta (classi diverse da qo) o theta+phi (qo-qo). theta=phi=0 e' il rivale nullo gia' usato in 003/004 (rimescolamento dentro il paragrafo).
- M2 (theta,phi): theta tarato sul conteggio osservato di adiacenze di stessa classe non-qo, poi phi sul conteggio qo->qo, entrambi sullo split di taratura.
- M1 (solo theta) = rivale: theta tarato sul totale delle adiacenze di stessa classe (qo incluso), phi=0.
- Taratura: griglia theta 0..3 passo 0,5 e phi 0..4 passo 0,5, 30 campioni per punto, interpolazione lineare, bloccata ai bordi della griglia.
- Predizione sull'altro split: MCMC Metropolis a scambi di due posizioni, burn-in 10n, distanziamento 3n, 200 campioni; intervallo = 2,5%-97,5% (v[5], v[194] dei 200 ordinati).
- Seme 20261121 (VOYNICH_SEED), solo random.random() di random.Random.

## Criterio di successo fissato nel codice (run.py) prima del run finale
SUPPORTED se, in ENTRAMBE le direzioni di taratura (0->1 e 1->0): (a) i tre conteggi osservati sullo split predetto (adiacenze non-qo di stessa classe, qo->qo, ripetizioni esatte della prima parola) cadono dentro l'intervallo predittivo di M2; e (b) il conteggio qo->qo osservato cade fuori dall'intervallo di M1. Altrimenti NOT SUPPORTED, indicando metrica e direzione. Nessun p-value: criterio di contenimento.

## Storia onesta
Il parametro phi e' stato introdotto dopo un run esplorativo precedente (precursore_esplorativo/) sugli stessi dati di training, in cui il solo theta sovrastimava qo->qo di circa 3 volte in entrambe le direzioni. Il test attuale (taratura su uno split, predizione dell'altro) non e' quindi confermativo per l'esistenza dell'effetto qo, gia' noto da 004; e' un test di sufficienza del meccanismo a due parametri.

## Limiti
Incertezza di theta/phi non propagata negli intervalli; convergenza MCMC non diagnosticata; conteggi qo->qo piccoli (2 e 12), quindi poca potenza e phi poco stabile tra split; classi per prefisso arbitrarie; ordine scambiabile dentro il paragrafo (ignora colonna, A/B, mano); nessuna calibrazione su generatore noto e nessun confronto con Timm-Schinner (richiesti da PROTOCOL.md v1: attempt NON qualificante); CI GitHub non ancora eseguita.
