# VOYNICH | ANCHOR-05, ANCHOR-06, ANCHOR-07
**Resoconto scientifico esplorativo, 12 novembre 2026. Nessuna decifrazione dichiarata.**

## Sintesi

- **ANCHOR-05 (negativo):** la coincidenza dei prefissi EVA di due caratteri fra etichette zodiacali adiacenti, all'interno delle metà di ciascun segno, non supera il controllo di rimescolamento (`19,90%` osservato contro `20,54%` atteso; `p=0,6637`, 20.000 permutazioni, 196 coppie, 7 segni). Questo non prova che i nomi di grado o i numeri siano impossibili; non vediamo la specifica firma morfologica semplice testata.
- **ANCHOR-06 (positivo strutturale):** nei 7 segni della serie iniziale, la somiglianza fra le prime 15 e le seconde 15 etichette del *medesimo segno* è superiore rispetto alle combinazioni fra segni diversi (`0,68653` vs `0,46290`, `p_esatto=1/5040=0,0001984`). Aggiungendo Scorpione e Sagittario, nei 9 segni si osserva `0,68134` contro `0,46216`, `p_esatto=2/362880=0,000005511`. Il recupero della metà corretta per massima somiglianza è `5/7` e `6/9`; non è una traduzione.
- **Sensibilità di trascrizione:** su IT2a di Takahashi, con metrica e assegnazioni identiche, il risultato è `0,64734` vs `0,43802` nei primi 7 (`p=0,0005952`) e `0,63201` vs `0,43350` nei 9 (`p=0,00001102`). Per le 270 etichette analizzate, 94 hanno il primo gruppo EVA diverso rispetto a ZL3b. L'effetto è relativamente robusto a queste variazioni, ma le due versioni derivano dallo stesso manoscritto.
- **ANCHOR-07 (controllo restrittivo su una stessa facciata, negativo al criterio richiesto):** per i 3 diagrammi di Leone, Vergine e Bilancia che condividono `f72v` (90 etichette), riassegnare casualmente le etichette tra i diagrammi mantenendo fisse le metà produce `p=0,03205` (ZL3b) e `p=0,20579` (IT2a); mescolare blocchi di 5 etichette dà `p=0,04530` e `p=0,24054`. Il criterio fissato prima del test di `p<0,01` su entrambi i null e in entrambe le trascrizioni **non è raggiunto**.

**Lettura scientifica:** è presente una struttura testuale riconoscibile nel materiale zodiacale anche attraverso due trascrizioni. La specificità di diagramma, tuttavia, rimane confondibile con posizione, modalità di scrittura e differenze fra pannelli. Nessun segno ha acquisito un significato semantico verificato. Questo è coerente con osservazioni precedenti di sigle/radici condivise nelle etichette zodiacali; l'effetto non va presentato come inedito.

## Metodi e provenienza

**Corpus:** ZL3b-n.txt, `411671` byte, SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`. IT2a-n.txt (Takahashi), `342104` byte, SHA-256 `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`. Entrambi sono stati recuperati dalla Library e verificati sui byte. Sono elaborati unicamente i loci `@Lz` o `&Lz`, prima sequenza `[a-z]+` dopo esclusione dei commenti IVTFF inline. Si conservano le differenze di trascrizione, senza forzare normalizzazioni storiche.

**Segni primari (tutti da 30 etichette):** Pesci `f70v2`, Ariete `f70v1 + f71r`, Toro `f71v + f72r1`, Cancro `f72r3`, Leone `f72v3`, Vergine `f72v2`, Bilancia `f72v1`. **Sfida aggiuntiva:** Scorpione `f73r`, Sagittario `f73v` (30 ciascuno). I due segni di sfida non erano stati usati in ANCHOR-04, ma non costituiscono un set strettamente cieco a livello del progetto. I loci di Gemelli hanno un numero diverso e non sono inclusi.

**Metadati:** l'ordine `1..30` è quello letterale IVTFF. Non è stato validato da revisori geometrici indipendenti che segua un ordine di grado astrologico. Nessun legame figura-etichetta è stato promosso a identificazione validata.

**ANCHOR-06:** per ogni metà di 15 etichette, si contano tutti i bigrammi e trigrammi EVA con sovrapposizione del primo gruppo testuale. Si normalizza il vettore per norma L2, quindi si calcola il coseno tra le 2 metà. Il valore osservato è la media sulla diagonale della matrice segno×segno, meno la media degli elementi fuori diagonale. Il test esatto riassegna le seconde metà ai segni: `7! = 5.040`, poi `9! = 362.880` permutazioni. Le statistiche e tutti i punteggi sono archiviati in `result.json` e `it2a_result.json`. Non si adattano pesi o parametri alla risposta. È un protocollo locale scritto prima di vedere il risultato ANCHOR-06; non un preregistro esterno e non corregge il fatto che altri esperimenti hanno già esplorato il materiale.

**Controllo pagina post hoc:** nella sequenza dei 9 segni le somiglianze fra metà del medesimo segno superano mediamente le metà dei segni immediatamente adiacenti di circa `0,099` in entrambi i corpus. Questo risultato è descrittivo: adiacenza zodiacale non equivale a prossimità fisica perfetta e la verifica è stata ideata dopo l'ispezione della matrice. Limitando le sole permutazioni alle tre unità sulla stessa facciata `f72v`, il matching completo fra tre metà ha `p=1/6=0,167` per ZL3b e `p=3/6=0,50` per IT2a, con scarsissima potenza (`3!` combinazioni). **Non è quindi dimostrata una separazione dalla variabilità legata al supporto materiale.**

**ANCHOR-07:** scelta una sola facciata fisica e tre pannelli con 30 labels ciascuno, calcolando la medesima differenza matched-vs-unmatched. Due null con 20.000 iterazioni ciascuno (seed 2026111207) preservano metà e facciata: (1) mescolamento delle 45 etichette tra i tre pannelli, in ciascuna delle due metà separatamente; (2) mescolamento di 9 blocchi di 5 etichette, sempre separatamente per metà. In tal modo si conserva parte della dipendenza locale che potrebbe produrre false «radici semantiche». La forma a blocchi non dimostra indipendenza grafica o semantica, e la scelta di f72v è stata motivata dal controllo precedente: è un test esplorativo, non una replica cieca.

### Valori e interpretazione

| Test | ZL3b | Takahashi IT2a | Status |
|---|---:|---:|---|
| ANCHOR-06, 7 segni, permutazioni esatte | 0,0001984 | 0,0005952 | Segnale strutturale |
| ANCHOR-06, 9 segni, permutazioni esatte | 0,00000551 | 0,00001102 | Segnale strutturale |
| Controllo 3 segni sulla facciata f72v (`3!`) | 0,167 | 0,50 | Inconcludente |
| ANCHOR-07, 90 etichette, shuffle fine | 0,03205 | 0,20579 | Non supera criterio |
| ANCHOR-07, 90 etichette, shuffle blocchi da 5 | 0,04530 | 0,24054 | Non supera criterio |

I test non sono pienamente indipendenti: tutti i confronti utilizzano lo stesso materiale e la ricerca ha eseguito diverse selezioni esplorative nel tempo. I valori p sono condizionati al rispettivo modello nullo, non probabilità di corretta interpretazione. In particolare, la figura zodiacale e il pannello sono perfettamente associati in questa base di dati.

## Reproducibilità

Python 3 con libreria standard: `python run_anchor05.py`, `python run_anchor06.py`, `python run_it2a.py`, `python page_control.py`. Per ANCHOR-07 serve anche NumPy: `python run_anchor07.py`. Gli script e i loro input sono inclusi nel pacchetto. Il confronto su copie di lavoro indipendenti ha prodotto risultati identici nei JSON principali (dopo la normalizzazione di un percorso assoluto nel report). I file originali sono conservati immutati e hanno SHA-256 registrati.

Lo stato di RC1.4.2 rimane **CLOSED_PENDING_VALIDATION**, RP-01 aperto, f085v irrisolto. Nessun builder, PCA, clustering o coupling vietato è stato eseguito.

## Decisione strategica

La ricerca statistica sulle etichette non è più la migliore destinazione delle risorse finché la relazione geometrica testo-figura non è certificata. Per una prova semantica non circolare bisogna: (i) correggere e certificare i crop che conservano figure e oscurano il testo; (ii) ottenere annotazioni visive indipendenti di caratteristiche osservabili; (iii) validare la relazione testo/figura con controllo per pagina, anello e pannello; (iv) fissare una predizione semantica su pagine non usate nello sviluppo; (v) cercare un riscontro iconografico in fonti storiche non Voynich. L'accordo fra revisori garantisce affidabilità dell'annotazione, non la verità della corrispondenza.

Nessun risultato qui autorizza la traduzione di una sequenza EVA, l'identificazione di un nome di grado o la promozione della geometria precedente a «ground truth».

## Riferimenti contestuali

- Rene Zandbergen, *Some special properties of labels in the Voynich MS*: https://www.voynich.nu/extra/labels.html
- V. Averyanov, *Thirty Names per Sign* (preprint indipendente): https://voynich.site/paper-2-labels?lang=en
- Yale Beinecke Library, MS 408: https://beinecke.library.yale.edu/collections/highlights/voynich-manuscript