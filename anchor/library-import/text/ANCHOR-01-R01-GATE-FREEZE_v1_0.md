# ANCHOR-01-R01-GATE-FREEZE · Specifica operativa 1.0

**Congelamento UTC: 2026-11-12T15:04:39.969890+00:00.** SHA-256 di questo documento e del contratto
JSON nei rispettivi sidecar e in `FREEZE_RECEIPT.json`. È un congelamento locale
prima delle nuove annotazioni di questo flusso, non una preregistrazione esterna
o un'attestazione temporale indipendente.

## Oggetto e limite scientifico

Questo gate confronta le regioni annotate da **due revisori indipendenti** sulle
due immagini pilota, non figure contro etichette. L'accordo misura riproducibilità
delle annotazioni, non verità del collegamento figura–testo. Il protocollo non
riusa i 30 esiti geometrici come etichette corrette.

Stato alla congelazione: `PREPARATION_DATASET_PENDING_VALIDATION`; nessun dato dei
due nuovi revisori ricevuto; esecuzione del gate `NOT_RUN`. I 30 esiti originali
restano `ambiguous`, zero link validati, attributo primario non selezionato,
H-A3R non eseguibile, RC1.4.2, f085v e RP-01 invariati.

## Insieme di soglie, senza scelta del migliore

| Dominio del passaggio | Soglie candidate in pixel nativi Yale |
|---|---|
| depicted_region, corpi/regioni figurative | 50, 100, 150, 200, 250 |
| glyph_region, regioni di glifi | 25, 50, 75, 100, 125 |

Si valutano **tutte le 25 combinazioni cartesiane**, non cinque coppie in
diagonale. Nessuna soglia è primaria. La griglia è una convenzione di sensibilità
proposta nella conversazione e fissata qui prima delle nuove annotazioni: non è
una stima dell'errore, non è rappresentativa di tutti gli errori plausibili e la
stabilità non è garantita al di fuori di questo intervallo.

Il registro delle 23 correzioni è conservato integralmente come storia
esplorativa verificata, con conclusione
`MATCHING_THRESHOLD_NOT_JUSTIFIABLE_FROM_CORRECTION_REGISTER_ALONE`.
**Non viene usato per calibrare questa griglia**, né si usano le distanze
primo–secondo vicino o la percentuale di univocità del pilota per sceglierla.

Le correzioni furono selezionate e prodotte dallo stesso operatore, in un contesto
non cieco con accesso a testi/lookup EVA. Non misurano variabilità inter-revisore
in condizioni cieche. Non è dimostrato che ogni singolo spostamento sia stato
causato da un prior testuale. La coda può comprendere riposizionamenti grossolani:
non se ne deducono automaticamente due popolazioni statistiche o soglie di identità.

## Matching deterministico

Confronto solo entro la medesima immagine e il medesimo passaggio di lavoro.
Il dominio è registrato prima della classe strutturale. Non si usa la classe
fine, il grado di confidence, un attributo, la lettura EVA o l'IoU per scegliere
le coppie. `high` e `medium` sono entrambi ammessi se lo stato è `present`.

Le annotazioni sono quadrilateri convessi in pixel della preview, origine alto
sinistra. Per A: 1449×1800 → 2979×3700 nativi; per B: 1336×1800 → 2793×3762.
Ogni asse viene convertito con il proprio fattore e quantizzato a 0,001 pixel
nativo, arrotondamento HALF_UP. Centroidi di area tramite shoelace, con aritmetica
razionale. Un bordo esattamente alla soglia è ammissibile.

Per ciascuna coppia di centroidi si confronta la distanza euclidea al quadrato
con il quadrato della soglia nativa, senza epsilon. Il costo è la distanza
euclidea divisa per la diagonale nativa dell'immagine, quantizzata a 10⁻⁹
(Decimal a 60 cifre, HALF_UP). Le parità sono definite su questi costi interi,
non su una pretesa uguaglianza di distanze reali non quantizzate.

L'obiettivo lessicografico è, nell'ordine:

1. massimo numero di coppie ammissibili;
2. minima somma dei costi interi normalizzati;
3. minima sequenza degli ID del secondo revisore assegnati agli ID ordinati del
   primo; il simbolo di non-match viene dopo qualsiasi ID valido.

Gli ID sono stringhe ASCII arbitrarie, univoche entro revisore e ordinate per
code point; non identificativi storici. Il solver Hungarian usa dummy e costi
interi con priorità separate: le parità del solver non cambiano l'assegnazione
canonica. Il codice e i test sono parte del payload congelato.

## Tassonomia, stati e confidence

`source_object_kind`: human_candidate, central_star, other_depicted_object,
text_region. Definizioni operative nelle istruzioni dei revisori, congelate con
le immagini. I domini non impongono la classe né filtrano discordanze di classe.
La κ è pertanto condizionata al passaggio e al matching, non una prova globale di
riconoscimento di tutto il manoscritto.

`annotation_status`: present, absent, ambiguous, not_localizable. Solo present
entra nel matching. Ambiguous e not_localizable rimangono nei denominatori di
copertura e F1 di concordanza come candidati non corrispondenti. Absent è una
nota negativa esplicita, riportata separatamente: in un inventario libero non
crea automaticamente un vero negativo o una casella attesa.

`confidence`: high = contorno visibile senza ricostruzione; medium = parzialmente
occluso/sbiadito ma inviluppo visibile delimitabile, con nota del bordo incerto;
low = delimitazione richiederebbe ricostruzione o scelta fra alternative, quindi
solo ambiguous/not_localizable. Per questi ultimi non si inventa un poligono.
Una regione ambiguous può conservare una proposta, esclusa dal matching.

## Metriche e criteri descrittivi

Si applicano separatamente a ciascuna delle quattro unità immagine×dominio,
senza compensare una pagina con l'altra. Le soglie sotto sono convenzioni
operative fissate qui, non stime empiriche o risultati inferenziali.

Siano N₁ e N₂ i candidati dichiarati (present+ambiguous+not_localizable), M le
coppie assegnate e U=N₁+N₂−2M. Si registrano anche assenze esplicite e conteggi di
ciascuno stato. Se entrambi omettono un oggetto, l'accordo non può rivelarlo.

| Componente | Criterio congiunto |
|---|---|
| Detection/copertura | F1=2M/(N₁+N₂) ≥ 0,90 **e** M/N₁ ≥ 0,90 **e** M/N₂ ≥ 0,90 **e** U ≤ floor[0,10×(N₁+N₂)] |
| Classification | Accordo grezzo delle classi ≥ 0,90 **e** Cohen κ ≥ 0,80, su tutte le coppie assegnate |
| Localization | Mediana IoU ≥ 0,70 su tutte le coppie assegnate, incluse quelle con IoU zero |

Non esiste una misura composita penalizzata. Le condizioni restano separate,
anche dove matematicamente ridondanti. Il limite sui non-match cresce col
denominatore dichiarato e non premia l'eliminazione silenziosa degli incerti.

Se N₁ o N₂ è zero, detection è INCONCLUSIVE, non un accordo perfetto. Classi
incerte sono escluse dal matching attraverso lo stato, ma rimangono nella
copertura. Per present la classe deve essere definita. Se M=0, classification e
localization sono INCONCLUSIVE. κ=(pₒ−pₑ)/(1−pₑ), con le quattro categorie;
se pₑ=1, κ è `NOT_ESTIMABLE` e classification è INCONCLUSIVE, non FAIL o PASS.
In particolare, una classe omogenea non prova affidabilità classificatoria.

Nessun intervallo di Wilson viene applicato a F1, κ o mediana IoU. Nessun
bootstrap per oggetto è presentato come incertezza tra folii. Tutte le metriche
sono `DESCRIPTIVE_ONLY`; variabilità tra folii `UNCERTAINTY_NOT_ESTIMABLE`.

## Precedenza della decisione in ogni cella

1. `PROTOCOL_INVALID`: payload alterato, consegne/attestazioni mancanti o
   incompatibili, esposizione a diagnostica dichiarata, confronto prima delle
   chiusure o violazione del contratto. Nessun risultato promuovibile.
2. `NOT_IDENTIFIABLE`: almeno una unità fallisce chiaramente detection o
   classification. Questo domina una classification INCONCLUSIVE altrove.
3. `INCONCLUSIVE`: nessuna insufficienza precedente, ma almeno una componente
   non stimabile o priva di dati. L'incertezza non viene convertita in FAIL.
4. `LOCALIZATION_BOTTLENECK`: detection e classification sufficienti in tutte le
   unità, ma localizzazione sotto soglia in almeno una.
5. `READY_FOR_V2_DESIGN / DESCRIPTIVE_ONLY`: tutte le condizioni applicabili
   soddisfatte in tutte le unità. Non equivale a un PASS inferenziale.

L'insufficienza è descrittiva rispetto a questo strumento, non un giudizio sulla
verità del collegamento né un'attribuzione di errore a un revisore.

## Stabilità della decisione sulle 25 celle

`PROTOCOL_INVALID` prevale sull'intera griglia. Altrimenti, se la decisione cambia
fra due o più celle, l'esito finale è **INCONCLUSIVE / THRESHOLD_SENSITIVE**,
con la tabella completa e senza scegliere la cella migliore. Se è identica in
tutte le celle, si conserva quella decisione con `THRESHOLD_STABLE`.
Una griglia stabilmente INCONCLUSIVE resta INCONCLUSIVE; una stabilmente negativa
non autorizza v2. Stabilità non significa necessariamente esito favorevole.

`READY_FOR_V2_DESIGN / INFERENTIAL_SUPPORT` è **irraggiungibile per costruzione
nel pilota a due folii**, indipendentemente dall'accordo osservato. Il codice
non dispone di un ramo che lo emetta. Anche la via descrittiva autorizza solo
la progettazione della futura regola, non H-A3R o la selezione del primario.

## Custodia, presentazione e chiusura

Immagini integrali, byte originali identici e istruzioni identiche. Ordine
A/depicted, A/glyph, B/depicted, B/glyph. Ruote complete, zoom consentito senza
modificare i file. I revisori vedono i glifi e il layout, ma non EVA, warning,
coordinate precedenti, ordinali, diagnostica, griglia o ipotesi H-A3R.

Il custode consegna **solo** `ANCHOR01_R01_REVIEWER_PACKET.zip`, conservando questo
pacchetto tecnico separato. Registra due ID pseudonimi distinti, attestazioni di
indipendenza e mancata esposizione ai precedenti risultati, hash del pacchetto e
del gate, UTC della consegna e della chiusura, hash dei due JSON definitivi.
I modelli di custodia sono vuoti: non sono prove di consegna o indipendenza.

Entrambe le chiusure devono precedere il confronto. Il controllo software
verifica byte, cronologia e attestazioni presentate; non certifica da solo che
due persone siano realmente indipendenti. Se emergono violazioni, il custode
registra PROTOCOL_INVALID anche se il controllo automatico non può rilevarle.

Solo dopo le metriche un terzo revisore può aggiudicare i conflitti. Dati grezzi e
metriche restano immutati; il consenso è un dataset distinto con propria versione
e provenienza. Nessuna modifica al contratto dopo la distribuzione. Qualsiasi
revisione richiede una nuova versione conservando questo congelamento e, per
nuovi criteri prospettici, nuove raccolte non esposte agli esiti precedenti.