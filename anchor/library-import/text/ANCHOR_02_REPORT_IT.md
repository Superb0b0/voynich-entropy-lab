# ANCHOR-02 | Ricognizione quantitativa e diagnostica geometrica
**Data:** 12 novembre 2026  
**Stato:** ESPLORATIVO, NON DECIFRAZIONE, NON TEST SEMANTICO VALIDATO  
**Perimetro indipendente:** nessuna modifica al ramo congelato RC1.4.2 (`CLOSED_PENDING_VALIDATION`), a `f085v` o al rilievo RP-01.

## Risposta operativa

La ricognizione recupera 239 etichette zodiacali in dieci pannelli (non dieci fogli fisici distinti) e sottopone la loro morfologia a controlli riproducibili. Nessuno dei due segnali investigati è convincente: i pannelli di uno stesso segno zodiacale non risultano più simili dei pannelli adiacenti, e i prefissi/suffissi di etichette consecutive non superano il controllo di ordine casuale. **Non è stata trovata una traduzione, una chiave, né una relazione semantica verificata.**

In compenso, la diagnostica applicata ai 30 candidati già preparati in ANCHOR-01 identifica 13 posizioni dove la revisione indipendente è particolarmente urgente. Questa priorizzazione è un risultato di triage, non una nuova assegnazione figura-etichetta approvata.

## Materiali e integrità

- Trascrizione: `ZL3b-n.txt` (IVTFF EVA-), 411.671 byte, SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; controllo calcolato effettivamente sui byte acquisiti in questa sessione.
- Inventario storico: `figure_inventory_corrected.csv` recuperato dal pacchetto `ANCHOR_01_GEOMETRY_PILOT.zip`. È un repertorio secondario e non una certificazione geometrica.
- Distanze congelate di ANCHOR-01: `all_candidate_distances.csv` (250 righe), `link_audit.csv` (30 casi), con la regola originale invariata.
- Immagini Yale di consultazione fornite nel pacchetto precedente: canvas 1006201 / 1006202. Alcuni crop sono incompleti e contengono frammenti testuali: **NON sono immagini cieche certificate**.

## Campione fissato

| Pannello | Segno visuale | Etichette Lz da ZL3b |
|---|---|---:|
| f70v2 | Pesci | 30 (inclusa etichetta della stella centrale, senza figura umana attestata) |
| f70v1 | Ariete (metà 1) | 15 |
| f71r | Ariete (metà 2) | 15 |
| f71v | Toro (metà 1) | 15 |
| f72r1 | Toro (metà 2) | 15 |
| f72r2 | Gemelli | 29 |
| f72r3 | Cancro | 30 |
| f72v3 | Leone | 30 |
| f72v2 | Vergine | 30 |
| f72v1 | Bilancia | 30 |
| **Totale** | **10 pannelli** | **239** |

`f73r` (Scorpione) e `f73v` (Sagittario) non sono stati inclusi nel calcolo. Tuttavia alcuni loro metadati ed esempi testuali sono stati visionati durante la ricognizione: **non sono un holdout strettamente cieco**.

## Esperimento A: il testo identifica il segno illustrato?

**Unità:** pannello zodiacale. **Segno noto:** identificazione iconografica, non traduzione del testo. Due soli confronti entro lo stesso segno (Ariete e Toro); entrambi fra metà di segno adiacenti, con 15 etichette per pannello.

Si estraggono trigrammi di caratteri EVA dai loci `@Lz` / `&Lz` e si costruisce un vettore TF-IDF non supervisionato per ciascun pannello. Si misura la media dei coseni per le due coppie di stesso segno.

- Coseno medio osservato (stesso segno): **0,307884**.
- Media degli appaiamenti di due coppie contigue senza sovrapposizione: **0,317047**.
- Test combinatorio di 28 appaiamenti disgiunti tra pannelli contigui: **p unilaterale = 0,571429**.
- Test di 630 appaiamenti arbitrari di due coppie disgiunte (non controlla la contiguità): **p = 0,204762**.

**Lettura:** nessun supporto positivo per una somiglianza testuale specifica al segno, nelle due sole coppie duplici disponibili. La bassa numerosità, l'adiacenza fisica e la differente lunghezza dei diagrammi impediscono conclusioni generali.

## Esperimento B: le etichette formano una progressione lungo il diagramma?

Si usa soltanto l'ordine dei loci nella trascrizione ZL3b, suddiviso in blocchi che iniziano con `@Lz`. Questo ordine **non è una mappa geometrica indipendentemente validata**. Sono 22 blocchi da almeno cinque etichette, che comprendono 238 delle 239 etichette (l'etichetta centrale isolata non ha una vicina ordinata).

Statistiche: numero di coppie consecutive che condividono i primi due o gli ultimi due caratteri del primo gruppo alfabetico; null ottenuto mescolando casualmente le etichette *solo dentro il relativo blocco*, 20.000 permutazioni, seme 20261112. Gli estremi del blocco NON sono considerati adiacenti, per non inventare una chiusura circolare.

| Misura | Osservato | Atteso dal null | p unilaterale (eccesso) |
|---|---:|---:|---:|
| Uguale prefisso di due caratteri | 49 su 216 contiguità | 48,643 | 0,503875 |
| Uguale suffisso di due caratteri | 16 su 216 contiguità | 14,892 | 0,418429 |

**Lettura:** nessuna evidenza di una progressione testuale locale rilevabile con queste misure. Questo NON esclude un codice numerico più complesso, né prova che gli ordini IVTFF equivalgano agli ordini spaziali veri.

## Controllo secondario: repertorio storico

Prima della trascrizione primaria era stato analizzato l'inventario Grove-Stolfi incluso in ANCHOR-01. Si è constatata una discordanza strutturale: l'inventario contiene 29 figure umane e una stella centrale in f70v2 e 30 figure candidate per Gemelli; ZL3b conta invece 30 loci Lz per f70v2 e 29 per Gemelli. Esistono inoltre differenze fra letture testuali. Queste discrepanze confermano che non è lecito equiparare automaticamente figura, etichetta e locus.

Nel controllo storico, la somiglianza fra i pannelli dello stesso segno non supera comunque il confronto fra pannelli contigui (p = 0,642857), e l'adiacenza dei prefissi non supera il null permutato (p = 0,502925). Questi valori sono sensibilità esplorative, non repliche indipendenti.

## Esperimento C: priorità geometrica sui 30 casi di ANCHOR-01

**Base congelata:** 30 loci, 30 corpi candidati, 250 coppie di distanza, **tutti 30 `ambiguous`** secondo la regola originale. La regola non è stata modificata e nessun caso è stato promosso.

Come diagnostica distinta, si calcola un'assegnazione globale a costo minimo uno-a-uno entro ciascun pannello/anello. Si verifica inoltre se la distanza del vicino più prossimo resta sotto il limite inferiore della seconda distanza nell'**intervallo di incertezza assunto dal pilota**, non empiricamente calibrato.

- **19/30** candidati con un margine locale che regge alla tolleranza numerica ipotizzata.
- **3/30** assegnazioni ottimali globali diverse dal vicino locale iniziale.
- **5/30** etichette con warning storico, che rimangono da verificare qualunque sia la distanza.
- **13 loci prioritari**, unione di casi senza margine stabile, warning e cambio di assegnazione: `f70v1.10`, `.11`, `.13`, `.14`, `.15`, `.16`, `.17`, `f71r.2`, `.3`, `.10`, `.11`, `.13`, `.14`.

L'algoritmo globale sceglie un abbinamento anche in presenza di ambiguità. **Il fatto che scelga non è evidenza che l'abbinamento sia vero.** Le coordinate provengono da un solo operatore; due revisori indipendenti dovranno controllare geometria, locus e corpo. La tavola `preliminary_figure_contact_sheet.jpg` è soltanto un controllo di qualità: alcuni ritagli troncano elementi necessari o contengono scrittura, quindi non è pronta per la codifica semantica cieca.

## Interpretazione complessiva

**Risultato negativo circoscritto:** due segnali semplici (firma lessicale del segno e sequenzialità locale di prefissi/suffissi) non emergono nei dati utilizzati. Questo riduce il valore di ulteriori tentativi di attribuire nomi/valori alle etichette in base alla sola somiglianza della trascrizione.

**Risultato operativo positivo:** 13 posizioni precise in cui investire prima il lavoro di ricognizione visiva. Non è un effetto semantico.

**Il test semantico vero non è stato eseguito:** manca ancora un insieme di associazioni testo-figura validate indipendentemente e un attributo visivo definito e codificato in cieco. Non dichiarare potenza, validazione o significato.

## Prossimo esperimento realmente falsificabile: ANCHOR-03

1. Doppia revisione indipendente, senza suggerimenti dell'algoritmo, delle 30 geometrie di f70v1 e f71r. L'identità del locus e quella del corpo vanno controllate separatamente; registrare disaccordi e casi non risolvibili.
2. Correzione delle finestre di ritaglio, eliminazione delle etichette visibili e valutazione di leggibilità; l'attuale tavola non soddisfa il gate di blinding.
3. Definire un unico attributo osservabile in modo riproducibile (ad esempio presenza/assenza di copricapo, se una verifica di fattibilità ne dimostra sufficiente variazione). Due codificatori non devono vedere il testo né la previsione del modello.
4. Solo allora verificare un’associazione predittiva su pannelli non usati per selezionare attributo o caratteristiche del testo. Permutare all'interno di pannello, anello e condizioni visive pertinenti, senza trattare le singole figure come repliche indipendenti.
5. Non proclamare una parola tradotta se emerge una dipendenza: serve ulteriore trasferimento intersezionale e conferma storica.

## Riproduzione

Il pacchetto ZIP contiene i file sorgente originali di questa ricognizione, i tre script per la parte quantitativa/diagnostica, l'esportazione per controlli manuali e i risultati JSON/CSV. Le librerie `numpy`, `scipy` e `Pillow` servono solo per l'ottimizzazione geometrica e i ritagli; le statistiche della trascrizione utilizzano la libreria standard Python. Il metodo è esplorativo: la scelta delle misure è stata raffinata durante l'analisi e le *p* non sono prove confermative preregistrate.