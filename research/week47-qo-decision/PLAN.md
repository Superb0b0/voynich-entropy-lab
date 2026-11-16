# WEEK47-QO-DECISION | piano decisionale 16–22 novembre 2026

**Stato: PROPOSTA OPERATIVA, NON UN NUOVO ESPERIMENTO ESEGUITO.**
**Obiettivo:** entro il 22 novembre ottenere un verdetto limitato, riproducibile e avversarialmente leggibile su **una** famiglia di spiegazioni per le regolarità `qo-`, oppure dichiarare con prova concreta `INCONCLUSIVE` / `NOT VERIFIABLE`. Non promettere decifrazione, traduzione o conferma indipendente del manoscritto.

## Fonti di autorità / divieti

1. Leggere gli issue [#22](https://github.com/Superb0b0/voynich-entropy-lab/issues/22) e [#23](https://github.com/Superb0b0/voynich-entropy-lab/issues/23) prima di operare.
2. G0 **CHIUSO CON ESCLUSIONI**; input canonico ZL3b `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`, parser RC1.2 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`, 4130 P / 35492 token / 6980 tipi. Mai introdurre le serie storiche escluse come comparabili.
3. Vecchio holdout pubblico **non indipendente**, nessun accesso o divulgazione di dati riservati, nessun uso su training. `RC1.4.2 CLOSED_PENDING_VALIDATION`; non sbloccare builder/PCA/clustering/coupling. GitHub Actions verde prova esecuzione, non validità scientifica.
4. Ogni ricercatore ChatGPT e ogni workflow deve riportare commit esatto, SHA input, parser, filtri, unità, dati di training/test, test negativi, stato CI **pertinente**, esposizioni pregresse e limiti. Nessun replay dello stesso output come “replica indipendente”.
5. Nessun `workflow_dispatch` di una nuova analisi prima che protocollo, generatori rivali autentici, versioni e *stesse regole applicabili a ciascun output* siano congelati e archiviati.

## Evidenze già verificate il 16/11

### QO-MECH-01: vantaggio predittivo della specifica Markov binaria NON SUPPORTATO

[Run Actions #43816088191](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43816088191), i due job `prepare` e `analyze` sono SUCCESS. Sorgente `tools/qo_mech_01.py` su `research/qo-isolated-replay-20261116`, Git blob `b52c5fe84efc976a20cc6e262e061741428c9062`. Il codice distribuisce le **foglie numeriche** con `SHA256("QO-MECH-01:"+numero_folio)%2`; allena sul gruppo 0 e valuta sul gruppo 1, poi viceversa. Le coppie valutate non vengono usate per stimare lo stesso fit. Tuttavia entrambi i gruppi provengono dal manoscritto già esplorato e non sono conferme indipendenti. Non è stato eseguito audit indipendente di ogni esclusione del preparatore.

Soglia protocollata: `mean_logloss(IID) - mean_logloss(Markov) >= +0.005 nat/coppia` in **entrambe** le direzioni; esito osservato `−0.00201135` / `+0.00996002`. Il criterio non è soddisfatto. La dicitura di script «falsificato» riguarda il criterio di questo *specifico* modello, non l'intera classe Markov né la struttura `qo-`. La divergenza fra direzioni suggerisce controlli per eterogeneità e potenza, non supporto all'ipotesi. **Inoltre il parser `qo_rival_calibration.py` non è RC1.2:** segmenta usando `*P/@P`, split iniziale su separatori `[.,\\s]+`, esclude le graffe con il contenuto e non segue necessariamente i blocchi IVTFF `<%>…<$>`. Ogni confronto numerico con EXP-SEQ-05 richiede riconciliazione metodologica **prima** del benchmark.

### Verifica globale NON VERDE

[Run #43818097211](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43818097211): `Verify archived attempts` FAIL; `001-paragraph-header-key` non ha `attempt.yml` quindi manca contratto esecutivo. Non silenziare il verificatore e non ricostruire il contratto retroattivamente per forzare verde. Etichetta `001: NON VERIFICABILE (LEGACY)`, isolata e datata, da discutere in modifica autonoma dopo audit. La CI specifica QO non sostituisce questa CI globale.

### Comparatore storico Timm–Schinner disponibile, ma non ancora pronto per una nuova CI

Nel **pacchetto utente** `ROUND4_EXP_SEQ_05_RESULTS.zip` (SHA-256 `5ddac5a65b881cc95985a9b85cd743991075b89859fd8d2ea894a513698bbba3`) vi sono 30 file `generator/seed_01.json` … `seed_30.json`, e `generator/recovered_manifest.json` (SHA-256 `647de23e3ef36c8c2f2e1e5c962c0b28408c206d3258c4d56c1889e254e36002`). L'inventario dei semi 1–30 è completo e ciascun campo `sha256` dentro i JSON coincide con il valore **riportato** nel manifest; **non** significa che il digest del file JSON stesso coincida né che sia stata rieseguita ora l'implementazione Java originale. Ricalcolare/attestare gli hash dei *payload* secondo la funzione originale prima di usarli come fonte esterna. Le uscite sono già state analizzate in Round 4: non sono dati nuovi o un holdout cieco.

## Unica domanda della settimana

**I profili delle aperture e le transizioni `qo-` del corpus canonicalmente segmentato sono distinguibili, con misure identiche e controlli espliciti della geometria, da modelli rivali realmente implementati (in primis il generatore originale Timm–Schinner e un controllo nullo con struttura comparabile)?**

Fino a nuova specifica operativa completa: `QUESTION_DEFINED / MODEL_COMPARISON_BLOCKED`.

Prima di eseguire occorre fissare:
- Metrica primaria su *blocchi IVTFF*, non «paragrafi» basati sui tag `@P`/`*P`; `qo-` = `first_alpha_token.startswith("qo")` dopo RC1.2. Distinguere incipit per posizione 1–2 contro 3–4 dall'endpoint transizione `qo→qo`: non scambiare i due risultati.
- Popolazione e filtri senza scelta sul risultato; se si usa 4–9 senza filtro, descriverlo come **riferimento descrittivo scelto nell'audit**, non preregistrazione provata. Riportare sempre tutte e quattro le sensibilità note.
- Regola di comparabilità dei generatori: distribuzione di righe per blocco e token per riga, possibile impossibilità di confronto A/B poiché i generatori non hanno etichette Currier, numero di semi e denominatori equivalenti; non scegliere matching ex post.
- Criterio numerico di distinzione e arresto, negativo plausibile, controlli per mano/quaderno e molteplicità. Il corpus Voynich già esplorato implica `EXPLORATORY` anche con PR datata.
- Sintesi di provenienza dei 30 output del generatore, versione/commit originale Java, configurazione, seme, algoritmo digest, hash per seme e comando di rigenerazione.

## Calendario con decisioni, senza quote artificiali di esperimenti

- **16–17 novembre:** revisione avversaria split `QO-MECH-01`, discrepanza parser, inventario 30 generatori; scegliere **un solo** confronto equo e definire cosa lo renderebbe informativo. Se non c'è comparabilità => `NOT VERIFIABLE` e nessuna nuova CI di test.
- **18–19 novembre:** congelare protocollo e input con hash/commit, realizzare runner deterministico sotto un *nuovo ramo esclusivo*, test sintetici, poi una sola esecuzione Actions a dati training autorizzati, soltanto se il gate passa.
- **20–21 novembre:** secondo replay (ambiente indipendente dove disponibile), confutazione, controlli negativi, CI di esperimento distinta da quella globale. Niente tuning della soglia sugli esiti.
- **22 novembre:** rapporto con esiti **SUPPORTED / FALSIFIED / INCONCLUSIVE / NOT VERIFIABLE**, per ogni specifico modello e perimetro; `SUPPORTED` significa *supporto esplorativo relativo al criterio fissato*, mai conferma del Voynich. In mancanza dei prerequisiti, rapporto negativo/inconclusivo documentato, non promessa di risultato futuro.

## Automazioni e qualità delle prove

- Automazione ChatGPT «Ricerca Voynich continuativa»: **sospesa 2026-11-16**; lo storico è conservato.
- Automazione «Controllo Voynich pubblico»: **giornaliera**, dalle 08:05 Europe/Rome 2026-11-17, avviso solo su cambiamenti verificati.
- Workflow `.github/workflows/autonomous-voynich.yml` **già pianificato giornalmente**, non va duplicato né scambiato per un agente scientifico. Le CI dedicate già esistenti sono un punto di partenza: eventuale nuova matrice di rivali solo con modello, input e metriche congelati.
- Dopo tre controlli improduttivi il gate si ferma; un umano non deve ricevere la stessa promessa riciclata. I modelli GPT producono ipotesi/codice, non audit indipendente del proprio output.

**Questa PR/branch conserva solo il piano e le evidenze già esaminate. Nessun esperimento nuovo, nessuna modifica ai gate, nessun risultato inventato.**


## ADDENDUM W47-FC-01 | Gate di comparabilità e arresto (16 novembre 2026)

**Questo addendum aggiorna le decisioni operative precedenti e prevale su ogni formulazione precedente che possa suggerire di eseguire il nuovo esperimento prima del superamento dei gate.** Non riesegue il manoscritto e non cambia i verdetti storici.

### 1. Distinguere verdetto interno da comparabilità

- `QO-MECH-01` **NON COMPARABILE con EXP-SEQ-05 / effetto posizionale `qo-`** finché il parser del test non coincide con RC1.2 e la delimitazione IVTFF `<%>…<$>`. Il risultato già verificato (`−0.00201135`, `+0.00996002` nat/coppia) resta soltanto **criterio interno di vantaggio Markov non raggiunto** sul precedente protocollo, e non rappresenta un'evidenza contro la struttura posizionale `qo-`.
- `qo→qo` fra righe consecutive, `qo-` come apertura nella posizione 3–4 e **ripetizione esatta della prima parola** sono tre endpoint diversi: nessuna sostituzione surrettizia. Un test su un endpoint non valida né falsifica gli altri.

### 2. GATE-PARSER: fail-closed (precede tutto)

Per dichiarare `PARSER_COMPATIBLE` occorrono **TUTTI** i seguenti controlli sul medesimo input ZL3b con hash canonico, senza accesso a holdout riservati:

1. Inventario strutturale di **740 blocchi IVTFF** identificati da `<%>` e `<$>`, con regole identiche per pagina, inizio, fine e casi incompleti; confrontare **ID e confini blocco uno per uno**, non soltanto il totale. La conta 740 è l'inventario strutturale dei blocchi, **non** il numero di blocchi eleggibili per filtri 4–9/6–10.
2. **4130 loci P, 35492 token, 6980 tipi** sul corpus completo e stesso hash RC1.2. Per ogni locus verificare stesso identificatore, stessi token puliti, appartenenza al blocco, ordine e regola di adiacenza; differenze elencate una per una con causa.
3. Nessun cambio retroattivo al parser canonico per far combaciare gli output; eventuale adattatore nuovo è **versionato e identificato da hash**, con test sintetici espliciti e distinzione fra coorte completa e training-only. Se il parser completo conta correttamente, il training-only può avere conteggi inferiori **per esclusioni documentate**, non deve artificialmente mostrare 35492 token.

Se manca un controllo, stato `PARSER_NOT_VERIFIABLE`; non partire con il confronto.

### 3. GATE-RIVALS: provenienza e confronto equo

- Timm–Schinner: usare i 30 output storici solo se sono **autenticati** rispetto a sorgente/versione/configurazione/semi/digest *e* se rigenerazione o provenienza verificabile ne consente un audit. Trenta file con 30 impronte riferite da un manifest non equivalgono a una rigenerazione confermata.
- Stabilire **prima dei risultati** come ottenere la stessa unità statistica: delimitazione dei blocchi, distribuzione delle lunghezze di blocco e di riga, inventario e denominatori, status delle classi Currier A/B. Se i generatori non possiedono classi comparabili A/B e non esiste un'etichettatura o matching difendibile **predefinito**, il confronto A/B non è lecito. Non inventare categorie per far passare il gate.
- Nulla vieta un confronto descrittivo non stratificato, ma soltanto se è progettato esplicitamente come **altro confronto**, senza riusare le inferenze A/B né proclamarne conferma. Se non ci sono rivali attestati con geometria confrontabile, segnare `RIVAL_NOT_VERIFIABLE` ed escluderli.
- Il precedente rapporto **O/E ≈0,08 per Voynich vs ≈3 per Timm–Schinner** è soltanto un **candidato di ipotesi già esplorata**, non risultato confrontabile finché non si verifica che osservati, attesi, modelli nulli, delimitazioni, campioni e denominatori sono davvero identici. Non trattare la somiglianza di denominazione O/E come identità statistica.

### 4. GATE-PRECOMMIT: blocco di esecuzione

Prima di qualsiasi nuovo risultato di confronto, **congelare e rendere verificabili su commit antecedente al run**:
`endpoint_primario`, `scope`, `input_sha256`, `parser_sha256`, `blocco_perimetro`, `rivali_e_versioni`, `null_model`, `soglie_numeriche`, `criteri_di_fallimento`, `controlli_negativi`, `molteplicità`, `seed`, `unità_cluster`, `politica_holdout`, `comando` e `output_atteso`. La CI deve validare schema e integrità prima dell'esecuzione, senza dedurre da un commit una conferma indipendente.

### 5. Stop automatico, senza eccezioni narrative

**Scadenza improrogabile di preflight:** **20 novembre 2026, ore 18:00, Europe/Rome**.

- Se a tale istante manca anche uno solo di `PARSER_COMPATIBLE`, `RIVALS_ATTESTED_AND_COMPARABLE`, `PRECOMMIT_VALID`, il confronto **NON PARTE**. La conclusione settimanale è `NOT VERIFIABLE — prerequisiti non soddisfatti entro la scadenza`, con elenco di ciascuna prova mancante, link e commit. Questo è un esito valido e non va aggirato spostando il deadline, cambiando l'endpoint o escogitando un rivale sostitutivo dopo aver guardato i risultati.
- Se tutti i gate sono soddisfatti, si autorizza **un solo** test, mantenendo la classificazione epistemica `EXPLORATORY` perché la famiglia di segnali era già nota. A fine test sono consentiti soltanto `SUPPORTED`, `FALSIFIED`, `INCONCLUSIVE` o `NOT VERIFIABLE` **per il modello e il criterio specifico**, non per una decifrazione.
- Lo stato `NON COMPARABILE` è un **flag metodologico di confronto trasversale**: finché presente blocca il nuovo test e porta a `NOT VERIFIABLE` alla scadenza. Non riscrive il verdetto interno di un test precedente.
- Nessun task orario GPT, nuova CI di test o replay numerico può attivarsi in forza di questo piano: attivazione solo dopo gate verificati. `main`, baseline G0 e RC1.4.2 restano immutati.

**Stato al 16/11/2026:** `QO-MECH-01 VS RC1.2 = NON COMPARABILE`; `PARSER_COMPATIBLE = PENDING`; `RIVALS_ATTESTED_AND_COMPARABLE = PENDING`; `PRECOMMIT_VALID = PENDING`; `NEW_EXPERIMENT = BLOCKED`.
