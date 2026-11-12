# VOYNICH — ANCHOR-03 / ANCHOR-04
**Rapporto esplorativo, 12 novembre 2026. Nessuna decifrazione dichiarata.**

## Risposta scientifica

I controlli completati **non forniscono una chiave semantica**. La migliore associazione fra pigmenti dei corpi delle 30 figure zodiacali dell'Ariete e caratteristiche della trascrizione ha `p_FWER=0,10134` su 80 confronti (20 caratteristiche testuali × 4 colori), con un'associazione numericamente estremamente elevata (`|r|=0,99661`) ma **fragile e quasi determinata da un solo caso raro**: nel gruppo f71r/outer, `cheary` è l'unica etichetta priva della lettera EVA `o`. È proprio in quel luogo che la maschera cromatica misura il verde maggiore. Il punteggio non giustifica l'interpretazione di `o` come nome di colore.

Un abbinamento **puramente angolare**, indipendente dall'ottimizzazione globale delle distanze ma basato sugli **stessi dati geometrici di un unico operatore**, ricostruisce invece esattamente 30/30 abbinamenti proposti dal matcher globale ANCHOR-02. Il risultato resta uguale dopo 81 perturbazioni del centro dei diagrammi per ciascuno dei quattro anelli (±40 pixel di anteprima in x e y, passo 10). La convergenza geometrica è un segnale **tecnico** che restringe la revisione, non una lettura indipendente dei grafemi e non promuove nessuno dei 30 rapporti a `validated`.

Il test ANCHOR-04 per verificare se gli stessi **numeri di grado** o posizioni ordinali lascino regolarità testuali fra sette segni (210 etichette) è negativo per tre misure (coseno di bigrammi+trigrammi `p_FWER=0,837`, prefisso a due caratteri `p_FWER=0,615`, suffisso `p_FWER=0,879`; 20.000 permutazioni per ciascun esperimento con controllo comune dei tre endpoint). L'esito contrasta una *firma morfologica semplice dell'indice 1..30*, non l'idea di nomi diversi associati a ogni grado, né codici con omofonia o rotazioni ignote. Gemelli (29 etichette) era escluso. Scorpione e Sagittario sono rimasti fuori dal test e non sono un holdout strettamente cieco per ragioni storiche di consultazione del materiale.

## Metodi ANCHOR-03: due rami separati

### A: colore della figura rispetto al testo

- 30 figure e 30 loci `Lz` di `f70v1` e `f71r`; 4 strati (folio × anello: 10+5+10+5). Testo dalla trascrizione originale ZL3b verificata SHA-256, non dal repertorio storico.
- Immagini Yale già archiviate nel pacchetto ANCHOR-01 (`1006201.jpg` e `1006202.jpg`): si contano pixel nel rettangolo dei `body_polygon` registrati, misurando rosso, verde, blu tramite soglie HSV **fissate prima del test**, e un conteggio totale dei tre colori. Queste misure **non dimostrano la tinta dell'abito**; catturano anche porzioni di altre zone illustrate.
- Codifica a priori di 20 caratteristiche binarie testuali: prefissi/suffissi frequenti, presenza di un insieme fisso di caratteri nel primo gruppo EVA, lunghezza e numero di gruppi alfabetici.
- Correlazione assoluta con centratura intra-strato. 20.000 permutazioni dei vettori-colore all'interno dei quattro strati, con maxT sui 80 confronti e correzione +1.
- Migliore prova: `has_char=o` vs `green` `|r|=0,996606`, `p_nominale=0,101345`, `p_FWER=0,101345`. Non significativo; effect size vicino a 1 è artefatto di leva di singola osservazione.
- Il colorimetro è vulnerabile a crop che tagliano il corpo, pigmenti antichi o aggiunti in epoche diverse, segmentazione per HSV e incertezza dell'abbinamento geometrico. Tutti i 30 abbinamenti sono **non validati**.

### B: controllo geometrico angolare

- Centro della ruota stimato tramite fit algebrico del cerchio sui dieci punti medi di corpi esterni di ciascuna pagina; nessun carattere Voynich visto dal matcher.
- Ordinamento angolare dei 5 o 10 corpi e delle 5 o 10 etichette di ciascuno dei 4 anelli; scelta del solo shift ciclico che minimizza la somma delle differenze angolari assolute.
- Esiti: allineamento 10/10, 5/5, 10/10, 5/5 con il matching globale distanza di ANCHOR-02. Shift ciclico 0, 4, 0, 0 rispettivamente. Il secondo shift costa 83,82–244,57 gradi cumulativi in più.
- Sensibilità sul **centro**, non sui poligoni individuali: in 81/81 prove per ciascun anello, 30/30 link rimangono uguali. Questo **non** simula errori di 12 pixel sui singoli poligoni, né verifica la lettura dei `Lz` scritti.

## ANCHOR-04: firma dell'ordinale nel registro zodiacale

- Sette segni completi: Pesci, Ariete, Toro, Cancro, Leone, Vergine, Bilancia; 30 loci per segno con ordine dei pannelli IVTFF nel corpus, Ariete e Toro concatenati seguendo l'ordine di folio. Nessuna ottimizzazione di offset o inversione.
- Per ognuna delle tre misure, somma media di somiglianze fra tutte le 21 coppie di segni nella stessa posizione (1..30).
- Null: rimescolamento indipendente delle posizioni **entro la metà 1..15 o 16..30** di ciascun segno, mantenendo differenze complessive fra due semicerchi; B=20.000, seed 2026111205; maxT across the three endpoint z scores.

| Misura | Osservato | Media null | p nominale | p maxT |
|---|---:|---:|---:|---:|
| Coseno (2–3 grammi, primo gruppo) | 0,077403 | 0,078192 | 0,551022 | 0,837208 |
| Prefisso identico (2 caratteri) | 0,141270 | 0,136756 | 0,332683 | 0,614519 |
| Suffisso identico (2 caratteri) | 0,049206 | 0,051204 | 0,611169 | 0,879456 |

**Conclusione limitata:** nessuna prova di una firma testuale ordinabile fine ripetuta per i 30 posti fra segni differenti **in questa orientazione del corpus**. Le etichette possono tuttavia riferirsi a nomi diversi per ogni segno, codici lunghi con omofonia o ordini ruotati. Non testare diverse rotazioni scegliendo quella migliore senza nuova penalizzazione per ricerca multipla.

## Preparazione revisione cieca: gate NON APERTO

È stato creato un kit di 30 ritagli delle sole regioni del corpo: prima di ritagliare, i 30 poligoni delle etichette **registrate** sono oscurati nell'immagine. Il codice segnala **10/30** ritagli con almeno una intersezione con un poligono di testo noto. Ciò non identifica tutti i possibili testi residui: altri segni del diagramma possono restare visibili, alcune mascherature occludono le figure. Inoltre i crop di origine troncano parti del corpo.

Di conseguenza: `MASKED_CANDIDATE_NOT_BLIND_CERTIFIED`; fogli per revisori R01 e R02 **vuoti**; nessun esito attribuito a revisori indipendenti. Le schede e le immagini sono materiale per una revisione successiva, non un test semantico in cieco completato. **NON consegnare l'archivio principale ai revisori**: contiene la chiave custode ID-figura e i testi. Esportare solo i pacchetti `ANCHOR_03_REVIEWER_*.zip` separati e verificare prima la qualità di ogni crop.

## Stato rispetto alla ricerca precedente

- RC1.4.2 rimane `CLOSED_PENDING_VALIDATION`; `f085v` irrisolto; RP-01 non risolto. Nessun parser congelato/import storico, builder, PCA, clustering o conditional coupling eseguito.
- Questo esperimento non è preregistrato su piattaforma terza né indipendente dagli altri tentativi; i p devono restare esplorativi.
- La letteratura (Averyanov, 2026, documento indipendente non peer reviewed) propone l'interpretazione dei labels come sigla di nomi di grado; questa è un'**ipotesi esterna**, non una conclusione del nostro test. La sua rettifica sul segnale al-Biruni è un buon esempio del pericolo dei confondenti in semicerchi.
- Yale raccomanda l'uso delle scansioni e limita l'accesso all'originale salvo proposte eccezionali: https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript ; https://ask.library.yale.edu/faq/174903 . Il preprint di Averyanov: https://voynich.site/paper-2-labels?lang=en .

## Cosa sblocca la prova semantica

1. Revisione **indipendente** testo-locus e figura-locus, con validazione della geometria e risoluzione/disaccordi espliciti; preparazione di crop puliti e sufficienti alla codifica.
2. Attributo VISIVO scelto con un protocollo stabile e codificato senza leggere testo o predizioni; due revisori, accordo misurato e casi incerti esclusi secondo regola prefissata.
3. Dataset multisezione con campione abbastanza grande; stima della potenza, null permutato rispettando pagina/ring e validazione fuori campione.
4. Una previsione semantica su pagine e fonti esterne non utilizzate nella costruzione delle classi; esperimenti contro sistemi generativi e codici storici concorrenti.

Non si è arrivati alla decifrazione. Sono stati però eliminati due possibili indizi facili e costruiti strumenti ri-eseguibili per controllare ipotesi senza creare falsi positivi.