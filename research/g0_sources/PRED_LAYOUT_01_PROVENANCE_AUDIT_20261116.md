# PRED-LAYOUT-01 | verifica di provenienza (2026-11-16)

**Stato:** ORIGINALE NON REPERITO, PRECEDENZA NON VERIFICABILE CON LE FONTI DISPONIBILI.

## Compito
Verificare se PRED-LAYOUT-01 fissò il perimetro «blocchi IVTFF di 4–9 righe senza filtro token» prima della rianalisi dell’effetto posizionale `qo-`. Questa nota non propone nuovi esperimenti e non interpreta un timestamp locale come deposito esterno.

## Ricerca eseguita
1. Lettura integrale degli issue centrali [#22](https://github.com/Superb0b0/voynich-entropy-lab/issues/22) e [#23](https://github.com/Superb0b0/voynich-entropy-lab/issues/23).
2. Ricerca per testo `PRED-LAYOUT-01`, `PRED-LAYOUT` e hash parziale `c9c54415` nelle risorse GitHub collegate e nei repository `Superb0b0/voynich-entropy-lab`, `Superb0b0/model-408-op` e `xenoglyph-ai/voynich-public`: nessun documento primario riconosciuto. Ricerca file nel branch pubblico `research/folio-predictive-benchmark-20261114`: nessun PRED-LAYOUT-01.
3. Ricerca nella Libreria per titolo, termini e metadati, compreso elenco completo dei nomi reperibili: nessun file denominato PRED-LAYOUT-01.
4. Inventario nomi e ricerca del riferimento testuale dentro gli ZIP disponibili `EXP_SEQ_05_RESULTS_EXPLORATORY.zip`, `ROUND2_EXP_SEQ_05_RESULTS.zip`, `ROUND3_EXP_SEQ_05_RESULTS.zip`, `ROUND4_EXP_SEQ_05_RESULTS.zip`, `ROUND5_EXP_SEQ_05_RESULTS.zip`, `EXP_SEQ_01d_mano_layout_controlli_dati_codice.zip`: nessuna occorrenza di PRED-LAYOUT-01 o `c9c54415`. Questa è ricerca sui materiali consultabili, non dimostrazione di inesistenza universale.

## Fonti primarie alternative recuperate, NON equivalenti a PRED-LAYOUT-01
- `PREREGISTERED_PROTOCOL.md` (EXP-SEQ-03 v1.0): SHA-256 `1b2daec07fc84697ce6a0e945258815f2fd4147857d7f0e9f52b78dc52b87c26`, 8706 byte. Testo dichiara congelamento locale il **10 novembre 2026**, dopo l'esame di A/B, con `EXTERNAL_TIMESTAMP_PENDING`. Perimetro **principale**: blocchi di almeno quattro righe e *prime quattro righe da 6 a 10 token ciascuna*. I blocchi 4–9 sono uno strato, non il campione primario senza filtro. Il testo stesso considera l'endpoint `qo-` già esplorato e non indipendente.
- `REPORT_B_REPLICATION_2026-11-10.md`: SHA-256 `0af1a7fed75a6cc6bf63f5777921fcd5ecc00e6a1c6feb97a51847ad793e63c6`, 3600 byte. Per confronto A/B usa **4–9 righe con filtro 6–10**, con outcome già conosciuto; data dichiarata 10 novembre 2026, non prova del diverso protocollo PRED-LAYOUT-01.
- `analysis.py` EXP-SEQ-05 originale: SHA-256 `4b40c6827b2d8520fe4f1fbdc1a3341298bc631b4242f037d1eebfec9a4b7773`. Riporta esplicitamente **almeno 4 righe senza filtro 6–10** nella sua analisi esplorativa; non prova la precedenza della selezione 4–9 senza filtro.
- Riferimento indiretto fornito dal revisore via utente: PRED-LAYOUT-01 avrebbe definito **4–9 righe senza filtro** per un quesito diverso (*posizione sulla pagina*), hash script incompleto `c9c54415…efb0`, timestamp sandbox, non esterno. **Non è una verifica del file originale, della data o dell'ordine degli esperimenti.**

## Decisione per l'articolo
- Non dichiarare che il perimetro **4–9 senza filtro** fosse preregistrato o formalmente principale per il test `qo-`.
- Può essere usato come riferimento **descrittivo dell'audit corrente**, se la scelta è motivata e si presentano in parallelo tutti e quattro gli scenari con denominatori e dipendenza fra confronti. Per eliminare ambiguità, preferire «perimetro di riferimento descrittivo» anziché «perimetro primario prefissato».
- Mantenere le analisi `qo-` **ESPLORATIVE** e senza replica indipendente. La riproducibilità tecnica e gli IC non cancellano la selezione storica.
- Se l'originale PRED-LAYOUT-01 riemerge, verificare integralmente byte, hash SHA-256 completo, data della prima registrazione e riferimenti esterni, eventuale versionamento e **quale endpoint** riguardava. Registrare con nuova revisione datata senza sovrascrivere questa nota.

**Nessuna modifica ai dati, alle baseline, ai gate RC1.4.2 o a G0 (chiuso con esclusioni).**
