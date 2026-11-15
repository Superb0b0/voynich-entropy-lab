# ANCHOR-02: preregistrazione della conferma indipendente (2026-11-15)

## Stato
**LOCKED_PENDING_GATE.** Documento registrato prima di qualsiasi accesso al campione riservato. Non costituisce un'autorizzazione ad aprire HOLDOUT.md o i fogli protetti. Nessun risultato di conferma è stato prodotto.

## Ipotesi primaria, direzione e criterio
Su folii mai usati nell'esplorazione, attribuiti indipendentemente alla mano 2, confrontare sezione biologica ($I=B) contro botanica ($I=H). Misura primaria: differenza tra le medie per folio della quota di token EVA che iniziano con la stringa letterale `qo`, **biologica meno botanica**. Ipotesi direzionale predefinita: differenza > 0. L'ipotesi nulla è differenza <= 0.

## Corpus e ammissibilità
Usare soltanto corpus con SHA-256 verificato in MANIFEST.md, su una partizione indipendente preesistente e sigillata. Le etichette di mano ($H=2) e illustrazione ($I=B/H) devono essere concordi in IT2a e ZL3b; folio intero è l'unità di assegnazione. Non utilizzare alcun folio già esposto in ANCHOR-01/02, neppure attraverso l'altra trascrizione. La lista degli ID protetti non deve essere stampata, esportata o ispezionata. L'accesso al campione riservato richiede una procedura di sblocco verificata, con audit degli accessi.

## Procedura congelata
1. Verificare hash e che nessun folio di conferma sia stato usato nei test esplorativi; produrre solo conteggi aggregati e un impegno crittografico sulla partizione.
2. Verificare in modo cieco che vi siano almeno 5 folii indipendenti per gruppo, con >=75 token validi per pagina, e almeno 10 pagine per gruppo. Se non soddisfatti: INCONCLUSIVE, senza ricalibrare i criteri.
3. Analisi primaria: quota `qo` per folio, aggregando pagine del medesimo folio; permutazione esatta delle etichette dei folii quando possibile, altrimenti 99.999 permutazioni con seme 20261115; p unilaterale con correzione +1. Soglia alpha=0,01, fissata prima di aprire il campione. Richiedere differenza positiva in entrambe le trascrizioni e p <= 0,01 per la prima trascrizione dichiarata primaria, IT2a. ZL3b è controllo di robustezza, non replicazione indipendente.
4. Analisi secondarie, senza cambiare la decisione primaria: standardizzazione della lunghezza in classi 1-3, 4-5, 6+; posizione nella riga primo/intermedio/ultimo; leave-one-folio-out; audit parser e marcatori editoriali.
5. Se il parser produce token da annotazioni editoriali, la prova è INCONCLUSIVE finché non esiste parser corretto, testato e preregistrato **prima** di aprire il campione. Non scegliere il parser sulla base dei risultati riservati.

## Gate obbligatori
- Workflow generale `.github/workflows/verify.yml` verde su commit congelato; test isolato verde non basta.
- Revisione indipendente di hash, parser, assegnazione per folio, integrità della partizione e assenza di leakage.
- Almeno 5 folii riservati per ciascuno dei due gruppi; se la partizione non lo consente, registrare **NOT_TESTABLE_WITH_CURRENT_HOLDOUT** e progettare un'altra fonte indipendente. Non spostare fogli esplorati nel campione di conferma.
- Una sola apertura del campione, con log e report firmato; non ripetere test fino a ottenere significatività.

## Interpretazione
PASS dimostrerebbe una differenza predittiva fuori campione, non il significato di `qo`, una traduzione, né una relazione causale con il contenuto. FAIL falsificherebbe la specifica ipotesi predittiva su questo campione. INCONCLUSIVE/NOT_TESTABLE non sono PASS.

## Stato alla registrazione
ANCHOR-02 esplorativo: IT2a e ZL3b hanno mostrato differenza positiva nella mano 2 con controlli per lunghezza e posizione; l'intero processo di verifica generale è ancora rosso. Campione indipendente non aperto; disponibilità di folii mano-2 H/B nel holdout non verificata. **Non riportare una conferma indipendente finché i gate non sono superati.**
