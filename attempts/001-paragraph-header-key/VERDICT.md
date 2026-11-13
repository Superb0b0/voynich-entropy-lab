# Tentativo 001: verifica eseguita, verdetto esplorativo NEGATIVO

[FATTO VERIFICATO da codice] SHA-256 corpus e parser coincidono con i lock; 4.130 loci P, 207 folii iniziali; 158 folii eleggibili, 619 paragrafi, 16.309 token corpo lunghi almeno tre.

[ESPLORATIVO] Split 0, 83 folii: osservato 0,221902, null 0,225669, O/E 0,9833, p=0,746, differenza CI95 bootstrap per folio [-0,013442, 0,005844]. Split 1, 75 folii: osservato 0,258175, null 0,233646, O/E 1,1050, p=0,002, CI95 [0,007494, 0,042443]. Segnale non replicato nei due split, criterio preregistrato FALLITO.

[ESPLORATIVO] Coincidenza esatta secondaria: split 0 p=0,7375, split 1 p=0,4145. Generatore rivale che rimescola i token nel folio: quote medie di prefissi 0,279469 e 0,272382. Le percentuali non sono una decifrazione.

[IPOTESI per la prossima pista] La divergenza fra split potrebbe riflettere Currier A/B, mano, sezione o dimensione di folio. Serve confronto predichiarato sui metadati esterni, non selezionare retroattivamente il gruppo favorevole.

[PROVENIENZA] Fonti: corpus e parser in experiments/line-memory/experiment/inputs; risultati originali EXP_SEQ_LINE_MEMORY_01 in experiments/line-memory; xenoglyph-ai/voynich-public consultato in sola lettura. Lo studio precedente EXP_SEQ_01h_blocchi_lessico è solo parzialmente disponibile sul branch staging e non ha testato questa metrica header/corpo a livello di folio.
