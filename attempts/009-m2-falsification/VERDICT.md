# 009 — risultato verificato e limiti

GitHub Actions run 43734949679, job 132875373961: SUCCESS. Artefatto results-ci-009 (ID 14170480430). Questo attesta esecuzione riproducibile della procedura, non validazione scientifica.

Il codice ha applicato M2 con i parametri gia' fissati in 005 ai dati ZL3b training-only, hash filtrato dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9.

| direzione | metrica | osservato | intervallo 95% | dentro |
|---|---|---:|---|---|
| fit0_pred1 | same-class runs >=3 | 23 | [10,25] | SI |
| fit0_pred1 | lag2 same-class | 207 | [204,257] | SI |
| fit1_pred0 | same-class runs >=3 | 21 | [16,34] | SI |
| fit1_pred0 | lag2 same-class | 360 | [333,394] | SI |

Verdetto locale: M2_PASSES_NEW_CHECKS (4/4). Stato scientifico: ESPLORATIVO. Non e' una conferma indipendente: stesso corpus impiegato per sviluppare M2.

**Controprova gia' nota, da non occultare:** Attempt 006, trascrizione IT2a, era NOT SUPPORTED: in fit0_pred1 il conteggio same_nonqo osservato 128 superava il limite superiore M2 di 127. IT2a non e' un testo indipendente, ma una trascrizione differente del medesimo manoscritto. Questa fragilita' limita ogni generalizzazione.

**Avvertenza di implementazione:** il codice 009 calcola i conteggi di triplette valide usando coppie adiacenti valide; prima di interpretare la statistica come run di 3 righe consecutive bisogna verificare anche la validita' della seconda coppia. Il controllo lag-2 va interpretato allo stesso modo. Finche' non c'e' audit della definizione, i 4/4 sono un risultato del codice, non una conferma piena delle metriche descritte.

CI generale del repository separatamente FAIL per problemi preesistenti di archiviazione. HOLDOUT non aperto.
