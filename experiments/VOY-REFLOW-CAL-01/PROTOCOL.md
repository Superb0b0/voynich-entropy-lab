# VOY-REFLOW-CAL-01 — Controllo sintetico del re-flow

**Versione:** v1, bozza per audit, NON CONGELATA. **Data:** 2026-11-24. **Stato:** BLOCKED_PENDING_AUDIT_AND_FREEZE. DIRECT-05 e L2 restano bloccati. Nessun dato sintetico generato, nessun fit o re-flow eseguito per CAL-01.

## 1. Domanda e perimetro

Un processo refrattario noto, indipendente dai confini di riga, conserva il guadagno predittivo delle aperture qo- quando si permutano le lunghezze delle righe? Il controllo è positivo rispetto alla presenza di una dipendenza sul flusso, non rispetto alla conservazione del guadagno: quest'ultima è una congettura da verificare. Un controllo negativo Timm–Schinner non qualificato non risolve questa domanda.

Evidenze già note: REFLOW-01 riporta R/R, rho -0,0770 e -0,0929, G0 circa 0,012 nat, k=0 su 1000 per ciascuna trascrizione; Timm–Schinner non passa H1. I risultati sono archiviati; replay indipendente e datazione del push storico restano da verificare. Non sono dati di conferma indipendente. Il presente studio calibra una sola implementazione D1, non tutte le alternative sul flusso.

## 2. Generatore D1-CAL (specifica completa proposta)

Per ogni paragrafo generare una sequenza di token sintetici binari: `qo` e `d` (segnaposto non linguistici). Il prefisso qo- ha lo stesso significato operativo dell'estimatore storico. Nessuna proprietà lessicale diversa è richiesta dal test binario.

Stato a_t: distanza in token dall'ultimo qo generato, troncata a R+1, prima dell'estrazione corrente. Inizializzare a=R+1. Usare p=0,20, R=12 token, fattore di inibizione f=0,05. A ogni passo estrarre U uniforme [0,1). Se a<=R, emettere qo quando U<p*f; altrimenti quando U<p. Dopo qo impostare a=1; dopo d impostare a=min(a+1,R+1). Scartare i primi 256 token (burn-in), quindi conservare esattamente T token, dove T è la lunghezza totale del paragrafo storico. Reset e burn-in per ogni paragrafo. Nessun reset al confine di riga. Il generatore non riceve lunghezze individuali, posizione di riga, folio, Currier o testo originale. T è l'unico vincolo geometrico in generazione; il modello non è indipendente dai paragrafi.

Dopo aver generato il flusso, un adattatore separato lo divide secondo le lunghezze originali delle righe, conservando folio, sezione e source_rows. Nessuna selezione dei flussi in base alle aperture. I parametri sono convenzionali, non stimati: R=12 è dello stesso ordine della mediana storica di 9 token per riga in entrambe le trascrizioni; p e f definiscono un processo fortemente refrattario. Non sono scelti per ottenere rho alto o per replicare G0. Frequenza e G0 sintetici saranno riportati senza imporre una corrispondenza al manoscritto; eventuale differenza limita la trasferibilità. Non effettuare tuning o pilot su questi parametri. Un fallimento H1 è un esito ammesso, non una ragione per modificarli.

## 3. Repliche e semi

Due geometrie, ZL3b (indice 0) e IT2a (indice 1), usate come template, non repliche manoscritte indipendenti. 20 realizzazioni indipendenti per geometria, r=1..20, 1000 re-flow per realizzazione, i=1..1000. Totale 40 realizzazioni e 40.000 re-flow, senza arresto anticipato. Generatore NumPy Generator(PCG64(SeedSequence([20261124,501,g,r]))); consumo in ordine dei paragrafi del JSON, un uniforme per token incluso burn-in. Re-flow: Generator(PCG64(SeedSequence([20261124,502,g,r,i]))). Bootstrap storico immutato (seme 20261122; 10.000 estrazioni). Separazione dei domini di semi. Nessuna sostituzione delle repliche fallite. Checkpoint ammessi solo per riprendere lo stesso identificativo e seme, con log; nessun riepilogo decisionale parziale.

## 4. Pipeline e validità

Riutilizzare le funzioni originali di predictor/run.py (features, predict, score), l'adattamento AST read_paragraphs di execute.py e reflow_one di round5/round5.py. Non eseguire il modulo storico al livello globale. Modelli rifittati per ogni trasformazione: predict(rows,[False,True],'target_qo',1e-3,1.0,previous_mode='qo_only'); cinque fold storici per leaf; nessun nuovo split e nessun tuning. Log-loss media per transizione. Verificare corrispondenza esatta dei fold e identità di ordine token e multinsieme lunghezze fra sintetico originale e trasformato. Conservare il vettore completo G_rf. Il predittore usa solo prev_qo e target_qo oltre alla baseline; i token segnaposto sono sufficienti per questa specifica misura. Non usare il ciclo d-q-y, né statistiche lessicali come risultati del controllo.

Prima di eseguire: audit del nuovo runner, hash di tutte le sorgenti, versioni ambiente, test tecnici di invarianza rispetto a segmentazioni alternative a parità di T e seme (solo dopo congelamento, prima dei risultati scientifici), registrazione remota del protocollo, runner e manifest; verifica remota dei byte e attestazione del momento di osservazione del commit. Non confondere data committer e data push. Se una sorgente manca o non coincide, STOP. Nessun accesso al holdout del progetto; geometrie storiche già esplorate. Questa calibrazione è sintetica, non una nuova validazione del manoscritto.

## 5. Regole per ogni realizzazione

G0 = log-loss base meno esteso; [L0,U0] IC bootstrap condizionale per foglia, m = media G_rf; rho=m/G0 se G0 non nullo; p=(k+1)/1001 con k=count(G_rf>=G0). Percentili 2,5 e 97,5 lineari. Applicare nell'ordine esatto di REFLOW-01:

1. I se H1 fallisce (L0<=0 o L0<0,25 G0), dati invalidi o meno di 1000 re-flow validi.
2. I (inversione) se P97,5<0.
3. R se p<=0,05 e rho<=0,25.
4. I (attenuazione intermedia) se p<=0,05 e 0,25<rho<0,75.
5. C (conservazione apparente) se p>0,05 e rho>=0,75.
6. I in tutti gli altri casi.

Nessuna inferenza di equivalenza; p è una misura di coda condizionata alla trasformazione, non un p-value formale. H3 non è parte della domanda CAL-01 e non viene eseguita. Registrare anche le realizzazioni che falliscono H1, senza selezione.

## 6. Decisione aggregata (soglie convenzionali proposte prima dei dati)

Per ciascuna geometria riportare H1 validi, C/R/I su tutte le 20 realizzazioni, frequenza qo totale e agli incipit, G0 e rho individuali, proporzioni con IC Wilson 95% descrittivi (condizionati al template e ai parametri). Denominatore sempre 20, anche con H1 fallito. Se errore tecnico non risolto, il risultato aggregato è INCOMPLETO, non un verdetto scientifico.

- CONSERVAZIONE FREQUENTE: almeno 16 C su 20 in ciascuna geometria, nessun R in alcuna. Supporta la capacità di osservare conservazione per questa specifica implementazione, non un test universalmente discriminante.
- CONTROESEMPIO: almeno una R valida. R è possibile anche senza regole dipendenti dalle righe. Se almeno due R indipendenti nella stessa geometria, segnalare anche ricorrenza del controesempio. Non implica che ogni D1 produca R o che il Voynich segua D1.
- NON QUALIFICATO: meno di 16 H1 validi su 20 in almeno una geometria, in assenza di controesempio valido; il controllo non è sufficientemente informativo. Eventuali controesempi validi restano riportati anche con bassa qualificazione.
- INCONCLUDENTE: ogni altra combinazione.

Precedenza: INCOMPLETO, CONTROESEMPIO, NON QUALIFICATO, CONSERVAZIONE FREQUENTE, INCONCLUDENTE. 16/20 e assenza di R sono criteri prudenziali scelti in audit, non garanzie di potenza o di un tasso di errore. Non usare i 40 casi come repliche indipendenti del manoscritto. Il confronto R/R manoscritto vs C sintetico è descrittivo e condizionale; nessuna esclusione di un'intera famiglia. Una calibrazione completa della discriminazione richiederebbe anche un controllo noto dipendente dalle righe; non è incluso qui e non autorizza L2.

## 7. Output e arresto

Manifest esecutivo con hash del codice e sorgenti, ricevuta remota, ambiente, log, 40 flussi sintetici o ricostruzione deterministica con hash, CSV per replica (geometria, realizzazione, reflow_id, seed, n_transitions, gain_nats, status, error), H1 individuale, riepiloghi numerici, classificazione separata, report con tutti gli esiti e archivio SHA-256. Conservare ogni modifica tecnica e ogni esecuzione fallita. STOP dopo il report: niente DIRECT-05, niente nuovo generatore, niente modifica del preprint. Eventuali revisioni scientifiche richiedono nuova versione, motivazione e nuova registrazione antecedente ai dati.
