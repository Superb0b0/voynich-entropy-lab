# ANCHOR-01 · Rettifica diagnostica v1.1

**Data:** 12 novembre 2026. **Stato:** `PREPARATION_DATASET_PENDING_VALIDATION`.

Questa rettifica è un'analisi **descrittiva e retrospettiva**. La regola geometrica congelata (raggio normalizzato 2,0), le coordinate e i 30 esiti ufficiali `ambiguous` non cambiano. Non si eseguono nuove assegnazioni, inferenza, annotazione cieca di attributi, né validazione indipendente.

## 1. Rettifica esplicita del conteggio «10 casi puliti»

La critica è fondata: i tre flag da soli lasciano **14**, non 10, casi. Il numero 10 citato nell'addendum precedente applicava un **quarto filtro**, che non era stato evidenziato abbastanza: stabilità dell'unicità sotto una tolleranza **ipotizzata**, non misurata indipendentemente.

| Passaggio retrospettivo a raggio ipotetico 0,5 | N | Motivo |
|---|---:|---|
| Un solo candidato geometrico | **22** | `n_within_r0p5 == 1` |
| Di questi, distanza nulla | 7 | Flag `distance_resolution_floor` |
| Di questi, warning di fonte | 3 | Flag `source_warning` |
| Di questi, primo vicino non reciproco | 0 | Flag `nonreciprocal_nearest` |
| Intersezione tra zero e warning | 2 | `f70v1.14`, `f70v1.16`; non vanno contati due volte |
| Unione dei tre flag fra i 22 | **8** | 7 + 3 + 0 − 2 |
| Unici **senza i tre flag** | **14** | 22 − 8 |
| Fra i 14, instabili sotto errore ipotizzato | **4** | `f70v1.10`, `f71r.6`, `f71r.8`, `f71r.11` |
| Unici senza flag **e stabili sotto errore ipotizzato** | **10** | 14 − 4 |

**Definizione esatta del quarto filtro**, calcolata su *tutti* i candidati di ogni locus nel file originale `all_candidate_distances.csv`:

- `possible_count = count(assumed_distance_norm_low <= 0.5)`;
- `guaranteed_count = count(assumed_distance_norm_high <= 0.5)`;
- `stable_assumed = (possible_count == guaranteed_count == 1)`.

L'intervallo originale è basato su ±24 pixel di preview come **errore combinato ipotizzato**. Non è un errore osservato fra revisori. I 10 casi **non** sono collegamenti probabili o validati; sono una sottoclasse descrittiva con un'ipotesi di sensibilità aggiuntiva. In futuro non usare la dicitura «casi puliti» senza questi qualificatori. La lista completa e i filtri per ogni locus sono in `derivation_22_14_10.csv`.

Sull'intero campione di 30 loci, i tre flag hanno cardinalità 10 (zero), 3 (non reciproco), 5 (warning); le sovrapposizioni sono 3 zero∩warning (`f70v1.13`, `.14`, `.16`) e 1 warning∩non reciproco (`f70v1.15`). L'unione è **14 loci distinti**, non 18. `review_flags_union.csv` esplicita tutti i casi.

## 2. Le dieci distanze nulle

Il controllo geometrico sui poligoni **originali** mostra che tutte e dieci le distanze 0,0 corrispondono a **intersezioni di area positiva fra poligono dell'etichetta e poligono del corpo**. Non sono mere tangenze dei poligoni così come registrati. Il file `per_locus_diagnostic_v1_1.csv` aggiunge `zero_distance_polygon_relation`, area d'intersezione e IoU.

Questo **non** dimostra che i tratti d'inchiostro dell'etichetta si sovrappongano al corpo reale. I poligoni manuali possono essere troppo ampi, includere contenitori o elementi occlusi. La colonna `zero_distance_cause` è quindi **`unresolved_pending_independent_visual_review`** per tutti i dieci. Le possibili categorie future (`overlap_plausible`, `polygon_too_coarse`, `unresolved`) richiedono giudizio visivo indipendente, non sono deducibili dalla sola distanza 0.

## 3. Distribuzione del secondo vicino

Quantili calcolati sui 30 valori **non arrotondati** del file originale con interpolazione lineare sull'indice `(n−1)p`:

| Statistica | Distanza normalizzata |
|---|---:|
| Minimo | 0,1485 |
| Q1 (25%) | 0,4074 |
| Mediana | 0,9045 |
| Q3 (75%) | 1,4358 |
| Massimo | 1,7976 |

L'istogramma è in `second_neighbor_histogram.csv`. La distribuzione è ampia, con una coda di secondi vicini molto prossimi, ma **la bimodalità non è dimostrata** da 30 osservazioni né dalla sola distanza fra quartili. Evitiamo di attribuire due popolazioni latenti senza evidenza.

## 4. Limiti e prossimo gate

- Il raggio 0,5 è **post hoc, esclusivamente descrittivo**. Nessuna nuova regola è adottata.
- I 30 esiti ufficiali restano `ambiguous` sotto la regola congelata 2,0.
- Nessun collegamento validato; nessun attributo visivo primario selezionato; nessun test inferenziale.
- `GEOMETRY_RULE_FROZEN v2` non va definita prima di un'effettiva revisione indipendente delle coordinate.
- La revisione deve separare rilevamento, classificazione e localizzazione, senza mostrare ai revisori la diagnostica, i primi vicini, i warning o il testo trascritto. Il materiale non annotato è nel pacchetto separato per revisori; le immagini contengono comunque i glifi originali e non sono cieche rispetto alla pagina visiva.
- **H-A3R non eseguibile; RC1.4.2 `CLOSED_PENDING_VALIDATION`, f085v e RP-01 invariati.**

## 5. Provenienza e riproducibilità

Verificati gli SHA-256 del ZIP pilota originale, della regola e delle coordinate contro `COORDINATES_LOCK.json`. Il codice `reproduce_clarification.py` rilegge **250 distanze**, 30 audit originali, 60 schede di revisione vuote e tutti i poligoni. La versione precedente non viene modificata. Per riprodurre:

`python reproduce_clarification.py --pilot sources/ANCHOR_01_GEOMETRY_PILOT.zip --prior sources/per_locus_diagnostic_original.csv --out /cartella/nuovo_output`

Dipendenza: `shapely>=2`. I file di origine sono inclusi nell'archivio completo. `SHA256SUMS` documenta i file derivati.