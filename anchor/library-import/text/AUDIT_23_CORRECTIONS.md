# ANCHOR-01-R01 | Verifica del registro delle 23 correzioni | Rapporto di sola lettura

**Esecuzione UTC:** 2026-11-12T14:50:27.168118+00:00  
**Stato:** `CORRECTION_REGISTER_VERIFIED / MATCHING_THRESHOLD_NOT_FROZEN`  
**Natura:** audit descrittivo del materiale esplorativo di un solo operatore. **Non** è validazione indipendente, non è stima dell'errore fra revisori e non è un nuovo gate.

## 1. Identità delle fonti

- ZIP sorgente originale `ANCHOR_01_GEOMETRY_PILOT.zip`: SHA-256 `e4e4aa74ed035f0bfb058f27c215fbd7ed7888952e2df43ce3a84939049edf42`.
- `35` voci del `SHA256SUMS` interno verificate sui byte dei file presenti nell'archivio.
- `coordinate_visual_revision.json`: SHA-256 `88f3b6c6033381d7820f0cb64f70d5a4e4ebf566b4d547fda28bb5bd945d7a1e`.
- `coordinates_draft_before_visual_correction.json`: SHA-256 `63f63d8e10f7ef8f9dc437d1347e8b13e453d32417c52da28852a1766c0c7f6c`.
- `coordinates_draft.json` finale: SHA-256 `458f5efed9591393c0b206a516a17a80282c4b6aba4ee850a87d3a08dd93e8ae`.
- Regola geometrica originale: SHA-256 `01b4313906fb5294a294d6949d7d52d5a6c1d522d8e237352257d06ce133cce4`.
- La corrispondenza degli hash prova coerenza interna con l'archivio acquisito, **non** provenienza esterna indipendente.

Attenzione: il file `corrections.csv` presente nell'archivio riguarda **una correzione dell'inventario storico** (`f72v1.Y.6`), **non** le 23 correzioni dei poligoni. Queste ultime sono registrate in `coordinate_visual_revision.json` e nelle due versioni complete delle coordinate.

## 2. Verifiche strutturali effettive

- 60 oggetti nella versione precedente e 60 in quella finale, con gli stessi ID.
- Esattamente **23** ID modificati, tutti e soli quelli elencati nel registro di revisione; **37** record invariati.
- Per ciascuno dei 23, i poligoni `old_preview_polygon` e `new_preview_polygon` nel registro coincidono esattamente con le rispettive versioni JSON.
- Nei record modificati cambiano esclusivamente i campi `polygon` e `preview_polygon`; gli altri campi sono invariati.
- Le coordinate native sono coerenti con il ridimensionamento IIIF/JPEG delle preview, entro l'arrotondamento di 0,001 pixel.
- Distribuzione delle correzioni: **12 corpi**, **11 etichette**; **9 su f70v1**, **14 su f71r**.
- Nessuna lettura di `link_audit.csv`, `all_candidate_distances.csv` o separazione primo–secondo vicino per questo controllo.

## 3. Metodo di misura

Per ogni ID modificato, sono stati letti **i due poligoni nativi Yale** (prima e dopo), calcolati i rispettivi centroidi di area con la formula di Gauss (shoelace) e misurata la distanza euclidea:

`shift_native_px = sqrt((centroid_new_x-centroid_old_x)^2 + (centroid_new_y-centroid_old_y)^2)`

I centroidi delle preview sono controlli di scala, non la fonte primaria. I quantili sono interpolati linearmente con indice `(n−1)p`. Nessuna normalizzazione mediante distanze tra figure/etichette, nessuna ricerca di una soglia che aumenti l'univocità.

| Categoria | n | Min px | Q1 px | Mediana px | Q3 px | P90 px | Max px |
|---|---:|---:|---:|---:|---:|---:|---:|
| Corpi | 12 | 12.3 | 140.5 | **204.6** | 265.4 | 408.0 | 421.0 |
| Etichette | 11 | 30.1 | 133.9 | **191.1** | 247.8 | 355.4 | 377.7 |

Le mediane delle due classi sono dello stesso ordine di grandezza **nei 23 interventi selezionati**, nonostante le dimensioni diverse degli oggetti. Non è una dimostrazione che le soglie di matching debbano coincidere.

## 4. Bias e limiti: perché NON congelare ancora una soglia numerica

1. **Selezione per errore riconosciuto.** Il registro comprende solo delimitazioni notate e corrette. Le imprecisioni non riconosciute non sono osservate; la distribuzione non rappresenta l'errore totale.
2. **Un solo operatore.** Le differenze bozza/finale sono revisioni dello stesso autore, non differenze tra annotatori indipendenti. La variabilità inter-revisore è `UNCERTAINTY_NOT_ESTIMABLE` da questo registro.
3. **Spostamenti anche ampi.** Correzioni di circa 200–420 px per corpi e fino a circa 378 px per etichette possono riflettere spostamenti grossolani, non normale jitter di localizzazione. Usare automaticamente un quantile di questi spostamenti come raggio per decidere «stesso oggetto» rischierebbe di associare oggetti distinti.
4. **Identità visiva non certificata.** Il registro mantiene lo stesso ID prima e dopo, ma ciò da solo non è una prova indipendente che i due contorni si riferiscano allo stesso oggetto fisico.
5. **Campione piccolo e raggruppato.** 12/11 correzioni distribuite su due folii, senza campionamento casuale e senza informazione sull'errore degli oggetti non corretti.

**Esito corretto:** registro recuperato e verificato; distribuzione degli spostamenti descritta; `MATCHING_THRESHOLD_NOT_JUSTIFIABLE_FROM_CORRECTION_REGISTER_ALONE`. Non viene proposto né congelato alcun valore in pixel. Un valore ottenuto dal registro, se adottato in futuro, andrebbe etichettato come euristica esplorativa, non come soglia empiricamente validata di identità.

## 5. Decisioni metodologiche per il gate, ancora in bozza

- **Localizzazione:** usare la congiunzione di copertura del matching, IoU delle coppie assegnate e conteggio dei non-match, ciascuno con soglia preregistrata. **Nessuna metrica composita pesata.** `ambiguous` e `not_localizable` non entrano nel matching e restano nei denominatori della copertura di annotazione, con conteggi separati.
- **Confidence operativa (bozza):** `high` = contorno interamente visibile, nessun tratto ricostruito; `medium` = contorno parzialmente occultato ma delimitabile con un tratto interpolato; `low` = contorno sostanzialmente ricostruito o con più tratti non visibili. Per `not_localizable` non si produce un poligono; la fiducia non ne sostituisce lo stato.
- **Classi strutturali:** `human_candidate`, `central_star`, `other_depicted_object`, `text_region`; non usare `container` come attributo primario implicito. `annotation_status` separato dalla classe.
- **Matching:** prima cardinalità massima delle coppie ammissibili, poi costo totale minimo di distanza tra centroidi, infine assegnazione lessicograficamente minima delle coppie di ID ordinati. Per un congelamento implementabile restano da definire quantizzazione numerica dei costi e soglie di ammissibilità **separate** per corpi ed etichette.
- **Inferenza:** `READY_FOR_V2_DESIGN / INFERENTIAL_SUPPORT` è **irraggiungibile nel presente pilota** con due folii. L'eventuale via descrittiva non equivale a validazione di link.
- **Precedenza:** `PROTOCOL_INVALID` > insufficienza chiara di detection/classification (`NOT_IDENTIFIABLE`) > `INCONCLUSIVE` > `LOCALIZATION_BOTTLENECK` > `READY_FOR_V2_DESIGN / DESCRIPTIVE_ONLY`.
- **Aggiudicazione:** solo dopo chiusura di entrambi i revisori e calcolo delle metriche; il consenso è un dataset separato che non riscrive le metriche.
- **Custodia:** stesse immagini integrali nello stesso ordine, stesse istruzioni e hash, senza EVA/diagnostica; chiusure UTC e hash dei due output prima di confrontare i risultati. Nessuna modifica retroattiva alla specifica dopo la distribuzione.

## 6. Stato invariato

`PREPARATION_DATASET_PENDING_VALIDATION`; 30 esiti ufficiali `ambiguous`; zero link validati; attributo primario non selezionato; H-A3R non eseguibile; RC1.4.2 invariato. **Accordo tra revisori = affidabilità delle annotazioni, non verità del collegamento figura–etichetta.**