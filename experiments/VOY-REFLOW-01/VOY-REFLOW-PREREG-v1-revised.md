# VOY-REFLOW-PREREG-v1 — Preregistrazione del test re-flow sul guadagno predittivo

| Campo | Valore |
|---|---|
| Versione | v1, revisione audit 1 |
| Stato | **REVISIONATA — NON CONGELATA.** Regole decisionali fissate; esecuzione bloccata fino al manifest sorgenti e alla registrazione remota (§10) |
| Data di redazione | 2026-11-24 |
| Redatto da | Claude, su richiesta di Roberto; revisione audit ChatGPT |
| Programma | VOY-DECIPHER-01 (stato: BLOCKED) |
| Corpora | ZL3b (parser RC1.2) e IT2a (Takahashi): stesso manoscritto, non repliche indipendenti |

## 1. Domanda

Il guadagno predittivo di «la riga precedente inizia con `qo-`» (≈ 0,012 nat per transizione, fuori campione per folio, già misurato su ZL3b e IT2a) resta quando i confini di riga vengono ridistribuiti (re-flow)?

Limiti di lettura, fissati prima del risultato:

- Se il guadagno si riduce o scompare, si osserva una dipendenza dai confini originali delle righe. Questo non mostra che la riga sia un'unità di cifratura: è compatibile anche con spiegazioni di pura impaginazione.
- Se un modello riproduce tutte le proprietà osservate, non ne segue che sia il meccanismo dell'autore: meccanismi diversi possono essere statisticamente equivalenti.

## 2. Quantità

Per ciascuna trascrizione T ∈ {ZL3b, IT2a}:

| Simbolo | Definizione |
|---|---|
| G0(T) | Guadagno sui dati originali, in nat per transizione: log-loss medio del modello base meno quello del modello con «qo- nella riga precedente». Stesso stimatore e stessi fold per folio dei modelli predittivi già eseguiti |
| [L0, U0] | Intervallo bootstrap per folio al 95% di G0 |
| G_rf(T,i) | Stesso guadagno sull'i-esimo re-flow, i = 1…N, con la procedura `reflow_one` di `round5/round5.py`. Modello base e modello esteso rifittati su ogni re-flow con gli stessi fold |
| m(T) | Media dei G_rf |
| P2.5, P97.5 | Percentili 2,5 e 97,5 dei G_rf |
| k | Numero di re-flow con G_rf ≥ G0 |
| p(T) | (k + 1) / (N + 1), unilaterale |
| ρ(T) | m(T) / G0(T): frazione di guadagno conservata |

N = 1000, fissato per tutte le esecuzioni H2; seme principale = 20261124 (scelta convenzionale precedente ai risultati). La derivazione dei semi e il metodo dei percentili (lineare) devono essere registrati nel manifest prima di eseguire; nessun arresto anticipato o sostituzione di repliche. I semi 1–30 del controllo Timm–Schinner restano invariati. La scelta di N sostituisce l’opzione condizionale dell’Appendice A.

## 3. Condizione di validità (controllo H1)

Per ciascuna T il test è valido solo se L0 > 0 (H1 riprodotto) e L0 ≥ 0,25 · G0 (precisione sufficiente perché le soglie su ρ non siano dominate dal rumore di G0). Altrimenti T è classificata INCONCLUDENTE per precisione (classe I); p e ρ vengono comunque riportati se definiti. La soglia è un filtro prudenziale convenzionale, non una garanzia di precisione di ρ.

## 4. Categorie di esito per trascrizione

Applicare le righe in ordine; la prima soddisfatta prevale. Nessuna categoria costituisce una prova di equivalenza, assenza di guadagno o identificazione del meccanismo.

| Categoria | Condizione | Classe |
|---|---|---|
| INCONCLUDENTE per validità | Controlli §3 o §8 falliti | I |
| INVERTITO (distribuzione prevalentemente negativa) | P97.5 < 0 | I |
| FORTE RIDUZIONE | p ≤ 0,05 e ρ ≤ 0,25 | R |
| ATTENUAZIONE INTERMEDIA | p ≤ 0,05 e 0,25 < ρ < 0,75 | I |
| CONSERVAZIONE APPARENTE | p > 0,05 e ρ ≥ 0,75 | C |
| INCONCLUDENTE | Tutto il resto | I |

Per ogni categoria riportare P2.5 e P97.5 e indicare se comprendono zero. Sono percentili della distribuzione dei re-flow, non un IC della media; includere zero non stabilisce assenza di guadagno.

Le soglie 0,25 e 0,75 sono frazioni convenzionali, non quantili empirici né conseguenze teoriche. La fascia intermedia non produce giudizi sui modelli. La conservazione apparente non stabilisce equivalenza: p > 0,05 può dipendere da bassa potenza. Il valore p è una misura di coda condizionata alla procedura di re-flow; la sua interpretazione come p-value formale richiederebbe una giustificazione di scambiabilità sotto il nullo, qui non fornita. Nessuna correzione multipla. La potenza è ignota; non si cambiano soglie dopo i risultati.

## 5. Modelli: definizioni operative e previsioni

| Modello | Definizione operativa | Previsione su G dopo re-flow | Conforme alla previsione se | Contrario alla previsione se |
|---|---|---|---|---|
| **A1** Codifica linguistica indipendente dalle righe | Sequenza di parole prodotta indipendentemente dalla segmentazione in righe; le righe sono applicate dopo | **Nessuna.** Senza una regola esplicita sulle parole in `qo-` non c'è una dipendenza sui token di apertura da prevedere, né conservata né ridotta | — | — |
| **B1** Cifrario con stato dipendente dalle righe | Lo stato (per esempio refrattario) viene aggiornato o azzerato al confine di riga | Forte riduzione: ρ ≤ 0,25 | R in entrambe le trascrizioni | C in entrambe |
| **C1** Sistema composizionale organizzato per righe | Ogni riga è un'unità con vincoli tra unità successive | Come B1 | R in entrambe | C in entrambe |
| **D1** Generatore autoregressivo sul flusso | Inibizione di `qo→qo` in funzione di distanza in token o stato del flusso; segmentazione in righe posteriore e indipendente dallo stato | Conservazione apparente: ρ ≥ 0,75 (congettura, non conseguenza necessaria) | C in entrambe | R in entrambe |

Dichiarazioni:

- **A1 è non discriminabile con questo test.** Nessun esito conta a favore o contro A1.
- **B1 e C1 non sono distinguibili** con questo test. Non esiste una giustificazione teorica per previsioni diverse e non ne viene forzata una.
- B1–D1 sono congetture quantitative associate a famiglie non completamente formalizzate. Il re-flow cambia i token campionati come aperture anche in un generatore indipendente dalle righe; né la conservazione dell’ordine né un raggio di inibizione lungo garantiscono la soglia di D1. Non si eseguono simulazioni D1 in questo protocollo.
- Un esito R è compatibile anche con spiegazioni non crittografiche di sola impaginazione. R indica soltanto conformità alla congettura B1/C1, non evidenza esclusiva a loro favore.
- Nessun modello viene promosso o escluso definitivamente da questo test.

## 6. Evidenze già note a chi scrive e a Roberto

Citate dalla conversazione di progetto, non ricalcolate in questa sessione.

| Evidenza | Valore |
|---|---|
| Ripetizione dell'apertura (osservata / attesa) | 6,96% / 13,62% (ZL3b); 6,80% / 13,52% (IT2a) |
| Informazione mutua delle aperture, z | +23,81 (ZL3b); +24,68 (IT2a) |
| Deficit congiunto di `qo-` righe 3–4, O/E: originale → re-flow | 0,28 → 1,14 |
| Ripetizione esatta della prima parola, O/E: originale → re-flow (ZL3b) | 0,082 → 0,143 |
| Ciclo d→q→y, quota in avanti | ≈ 63–66% (manoscritto); 51,1% (Timm–Schinner) |
| Guadagno predittivo G0 | ≈ 0,012 nat in entrambe; IC bootstrap per folio interamente sopra zero (ampiezza non nota a chi scrive) |
| Caso 3→4, ripetizioni di `qo-` | ZL3b: 109 casi, 18,85 previste dal modello base, 4,98 col `qo-` precedente, 5 osservate (O/E ≈ 0,27); IT2a: 112 casi, 19,46, 5,11, 5 (O/E ≈ 0,26) |
| Contrasto prima/seconda parola per `qo` | −0,286 (ZL3b), −0,282 (IT2a) |

**Non noti** a chi scrive, a Roberto e a chi esegue: tutti i valori G_rf, la loro dispersione, e ogni esito del test sul guadagno sotto re-flow.

Uso di queste evidenze: hanno informato la formulazione dei modelli e **non** possono essere citate come conferma indipendente. Il test sul guadagno non è del tutto indipendente dal Round 5: il caso 3→4 è lo stesso fenomeno del deficit congiunto. Le previsioni di B1 e C1 (esito R) sono quindi poco rischiose. La previsione di D1 (esito C) è in direzione opposta alle aspettative informate dal Round 5, ma resta una congettura non derivata da un modello formalizzato. **Aspettativa dichiarata di chi scrive:** più probabile R che C, senza probabilità quantificata.

I tentativi 005 (`SUPPORTED`, ZL3b) e 006 (`NOT SUPPORTED`, IT2a) sul modello refrattario specifico per `qo` risultano dallo storico del progetto ma **non sono stati verificati sugli artefatti**. Non entrano in questa preregistrazione.

## 7. Esiti fra ZL3b e IT2a

- R/R o C/C: concordanza decisionale; applicare §5.
- R/C o C/R: discordanza decisionale; nessun giudizio sui modelli. Riportare separatamente e discutere la possibile sensibilità alla trascrizione.
- Almeno una I: decisione congiunta sospesa per inconcludenza, non automaticamente discordanza. Due I sono due esiti inconcludenti.
- Riportare sempre categorie, valori e motivi separatamente; nessuna trascrizione privilegiata a posteriori. Non sono repliche indipendenti.

## 8. Condizioni di arresto e inconcludenza

Prima di ogni calcolo verificare disponibilità e SHA-256 di corpus, parser, codice predittivo, assegnazione dei fold per folio, `round5/round5.py` con `reflow_one`, output Timm–Schinner per i semi 1–30 e ambiente software. Registrare nel manifest anche la derivazione dei semi, la procedura bootstrap originale e l’aggregazione originale del controllo. Se un elemento manca o non è identificabile, STOP prima dell'esecuzione: non ricostruire a memoria e non sostituire lo stimatore.

Dopo l'avvio, qualsiasi re-flow non definito o mancante rende la relativa serie inconcludente; riportare identificativo e causa, senza sostituzione. Sono richiesti tutti i N = 1000 re-flow validi per ciascuna serie. Media, percentili e p decisionali si calcolano solo su serie complete; su serie incomplete eventuali statistiche dei soli validi sono descrittive e non decisionali, con denominatore esplicito. Fallimento del §3 o divergenza di fold, stimatore o procedura rende il risultato non utilizzabile per decisioni. Le restanti condizioni di inconcludenza sono nel §4.

H3 si esegue per la singola trascrizione soltanto se il controllo §3 passa, la serie H2 è completa e valida, m < G0 e p ≤ 0,05. Non richiede classe R; resta esplorativa. Un calo dopo l’aggiunta delle covariate non identifica una spiegazione causale.

Nessuna esecuzione aggiuntiva a parità di ipotesi; ogni modifica dopo congelamento richiede v2 motivata, conservando v1 e i suoi esiti.

## 9. Previsioni confermative ed esplorative

**Confermative**, nel senso limitato di «soglie congelate prima di conoscere il risultato», non di «ipotesi indipendente dal Round 5»:

- la classificazione del §4 per ciascuna trascrizione;
- la conformità alle congetture del §5 per B1, C1 e D1 e la regola di concordanza del §7.

**Esplorative**, senza soglie né previsioni preregistrate:

- H3 del protocollo (aggiunta di lunghezza e classe dell'ultima parola della riga precedente): nessun modello assegnato;
- controllo negativo Timm–Schinner (semi 1–30): si riportano G0, G_rf e, se già prodotto dallo script, il segno del coefficiente di `qo-` precedente. Un coefficiente negativo da solo non stabilisce equivalenza. Applicare l’aggregazione originale già documentata, senza introdurre una nuova aggregazione; riportare anche risultati per seme se disponibili nella procedura originale. Se l’aggregazione originale non è identificabile, STOP prima dell’esecuzione;
- il segno del coefficiente nel manoscritto, atteso negativo (coerente col deficit già noto, quindi non una conferma);
- qualsiasi scomposizione per tipo di transizione (1→2, 2→3, 4→5, 5→6): non eseguita in questo protocollo.

I p non sono corretti per confronti multipli. ZL3b e IT2a non sono due test indipendenti. La scelta di `qo-` è post hoc. Il holdout non è indipendente per le ipotesi sviluppate nei Round 2–5.

## 10. Integrità e datazione

- Dopo l'audit si calcola l'SHA-256 del file definitivo. L'hash non può stare dentro il file che identifica e viene registrato a parte.
- Il file viene committato su un ramo esistente, senza aprirne uno nuovo. Fa fede la data di push visibile su GitHub: la data di autore di un commit si può impostare localmente.
- SHA-256 consente il controllo d’integrità rispetto a un digest registrato; il timestamp locale non certifica la data di preregistrazione. Prima dei calcoli registrare anche il manifest delle sorgenti e dei parametri su un ramo esistente con evidenza remota della data di ricezione. Nessun risultato G_rf è stato consultato nella revisione audit.
- Nessuna modifica retrospettiva di soglie, definizioni o categorie. Ogni modifica genera una v2 con elenco delle differenze. v1 e i suoi esiti restano riportati.
- Dichiarazione di conoscenza: il file è stato scritto conoscendo ciò che compare nel §6 e non conoscendo alcun G_rf.

## Appendice A — Prompt di esecuzione (testo invariato)

```
RUOLO
Sei un esecutore di analisi. Questa chat ha UNA sola domanda e UN solo test. Non aggiungere varianti, soglie, prefissi, sottoinsiemi o confronti non elencati qui. Se ritieni utile un test in più, scrivilo come proposta in una riga a fine report e non eseguirlo.

DOMANDA
Il guadagno predittivo di "la riga precedente inizia con qo-" (circa 0,012 nat per transizione, fuori campione per folio, già misurato su ZL3b e IT2a) dipende dalla disposizione fisica delle righe oppure resta quando i confini di riga vengono ridistribuiti?

DATI E CODICE
- Corpus: ZL3b (parser RC1.2) e IT2a, gli stessi dei modelli predittivi già eseguiti. Usa gli stessi fold per folio e lo stesso stimatore del guadagno (log-loss medio per transizione, modello base meno modello con qo- precedente).
- Modello base: posizione di riga, lunghezza del paragrafo, gruppo Currier.
- Re-flow: usa la procedura `reflow_one` di round5/round5.py (token del paragrafo in ordine, lunghezze di riga permutate, flusso diviso di nuovo). Se il file non è disponibile, FERMATI e dichiaralo; non reimplementare a memoria.

IPOTESI E CRITERI (fissati ora, prima di eseguire)
H1: il guadagno medio sui dati originali è > 0 con IC bootstrap per folio al 95% interamente sopra zero (già osservato; riesegui come controllo).
H2: il guadagno medio nei re-flow è inferiore a quello originale. Calcola il guadagno su N re-flow (N = 1000 se il tempo lo consente, altrimenti 200; dichiara quale) e riporta media, deviazione standard e p empirico unilaterale = frazione di re-flow con guadagno >= originale, con correzione (k+1)/(N+1).
H3 (solo se H2 è sostenuta): aggiungi al modello base due covariate della riga precedente: la lunghezza in token e la classe dell'ultima parola (prime due lettere EVA). Riporta il guadagno di qo- precedente sopra questo modello esteso, sui dati originali.
Lettura: se il guadagno scompare nei re-flow, la dipendenza è legata al layout. Se resta, è una regola sul testo. Se H3 lo azzera, la dipendenza è spiegata dalla lunghezza o dalla parola finale della riga precedente.

CONTROLLO NEGATIVO
Ripeti H1 e H2 sull'output del generatore Timm–Schinner già disponibile (semi 1–30), senza ripeterlo su altri semi.

REGOLE
- Nessun numero che non provenga da codice eseguito in questa chat. Per ogni cifra: tabella con trascrizione, N transizioni, stima, IC o p.
- Nessuna riscrittura del metodo di stima dei fold. Nessuna scelta di soglia dopo aver visto i risultati.
- Vietati "significativo", "dimostra", "spiega il meccanismo". Dichiara che la scelta di qo- e dell'ipotesi è post hoc, che ZL3b e IT2a non sono indipendenti e che i p non sono corretti per confronti multipli.

USCITA
Un solo file .md con: (1) tabella H1, (2) tabella H2 con N dei re-flow, (3) tabella H3 se eseguita, (4) tabella del controllo Timm–Schinner, (5) tre righe di lettura secondo i criteri sopra, (6) SHA-256 dei file di codice usati. Poi STOP: niente proposte di nuovi round.
```

## Appendice B — Integrazione operativa vincolante

L’Appendice A è conservata letteralmente come traccia storica. In caso di conflitto prevalgono §§2–10 e questa appendice: N = 1000, seme principale = 20261124, criteri di validità, attivazione H3 e lettura non causale. Non cambiano il modello base, lo stimatore, i fold o `reflow_one`.

Oltre al report Markdown, produrre CSV completo con `corpus,reflow_id,seed,n_transitions,gain_nats,status`; per il controllo aggiungere `generator_seed`. Registrare errori, seme principale, derivazione dei semi, N, ambiente, metodo dei percentili e hash sorgenti. L’esecutore riporta i numeri senza classificare i modelli; la valutazione applica il §4 separatamente. Conservare i risultati del controllo Timm–Schinner con l’aggregazione originale verificata nel manifest. Nessun nuovo test.
