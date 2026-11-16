# W47 | Recupero prove mancanti, 16 novembre 2026

**Rapporto tecnico verificabile, non approvazione scientifica.** Branch `research/week47-qo-rivals-plan-20261116`, [PR draft #26](https://github.com/Superb0b0/voynich-entropy-lab/pull/26). Non aprire `HOLDOUT.md`. Gli identificativi della partizione riservata e i token non sono riportati qui. Il protocollo congelato e il branch `main` restano invariati.

## 1. Provenienza della partizione W47: prova tecnica recuperata

**CI PASS** [run #43889943078](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43889943078); riconfermata sul head [#43891726888](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43891726888).

- Implementazione autonoma: `research/week47-qo-decision/partition_policy_provenance.py`; test sintetici separati `tests/test_week47_partition_provenance.py`; workflow `.github/workflows/week47-policy-provenance.yml`.
- Sorgente storico del selettore `tools/make_holdout.py` (Git blob `7987a4b70fc1c78735beb69ffb8745b6edfd16ff`, SHA-256 `1494d75c0e896e53a2dce414d287bf2c1fa70a8bccff2e19617e5579bafa2e75`); policy letterale W47 `tools/qo_rival_calibration.py` (Git blob `f06bbf1d3ed8357153d634cc424e65966d184625`, SHA-256 `f21d87d56c6afe51e380de422cad0b3d69fe1428a25d58ae4bec2b54e6e09c00`).
- Corpus ZL3b SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; sorgente selettore seme `20261114`, frazione `0.20`, 3 strati, 102 folii candidati, 21 esclusi.
- **`REPRODUCED_SELECTOR_MATCH`**: insieme ricostruito algoritmicamente e costante letterale W47 coincidono esattamente. Nel job non è stato aperto/scritto `HOLDOUT.md`, non sono stati esportati identificativi o testo. Artefatto originario aggregate-only `w47-partition-provenance.json` SHA-256 `b891d2d6fef4384d6bd25f85196ef7fe61833f53ab536c57cccd42a708e42496`.
- **Limite:** non c'è confronto diretto con il contenuto di `HOLDOUT.md`, né timestamp esterno credibile che renda i folii scientificamente inesplorati. Il MATCH dimostra soltanto la derivazione della selezione codificata.

## 2. Controllo indipendente di token, blocchi e coppie: prova tecnica recuperata

**CI PASS** [run #43890720695](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43890720695); confermata sul head [#43891727085](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43891727085).

- Seconda implementazione `research/week47-qo-decision/parser_parity_independent.py`, confrontata con RC1.2 canonico (SHA-256 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`) e `structural_audit.py` mediante hash e confronto interno degli elementi.
- **ZL3b:** 4.130 loci P, 35.492 token, 6.980 tipi, 740 blocchi, 3.281 coppie eleggibili, 4.117 loci nei blocchi e 13 fuori. **IT2a:** 4.118 P, 34.510 token, 7.088 tipi, 772 blocchi, 3.307 coppie, 0 P fuori dai blocchi.
- Identità per locus/token e concordanza di contorni di blocchi e coppie: **0 discrepanze** su ciascuna traslitterazione nella verifica del secondo codice. Nessun marcatore di blocco spurio rilevato all'interno dei commenti.
- **672 blocchi comuni, 2.897 coppie comuni.** La traslitterazione IT2a NON è un corpus indipendente, né è identica alla ZL3b completa.
- Nessun identificativo/token o tabella dei folii riservati è stato esportato. L'artefatto aggregate-only `w47-independent-parser-parity.json` ha SHA-256 `281d2ab0defce126523ab68cbd83e9ce71c06d0bf440997fa97f29d459a1fd55`.
- **Limite:** seconda implementazione autonoma nello stesso ecosistema di codice/CI, **non** validazione di un revisore scientifico terzo, non prova di parità fra tutti gli input filtrati del futuro test o di indepen­denza semantica.

## 3. Controllo matematico del runner: prova tecnica recuperata

**CI PASS** [#43891315289](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43891315289), riconfermato sul head [#43891726817](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43891726817).

- `research/week47-qo-decision/runner_oracle_audit.py` verifica il valore teorico esatto della ripetizione di prima parola sotto permutazione entro blocco usando **solo parole artificiali**. Esito: aspettativa analitica `20.0000`; stimatore Monte Carlo del runner, con 10.000 permutazioni, `19.9554`.
- PASS anche sui controlli di denominatore, bootstrap di folio, casi limite e classificazione `SUPPORTED/FALSIFIED/INCONCLUSIVE`.
- **Limite:** test di correttezza sintetica, non audit umano indipendente del runner completo, nessuna stima O/E del Voynich, nessun calcolo scientifico su corpus protetto.

## 4. Checkout-free per il job scientifico: isolamento architetturale dimostrato

**CI PASS** [#43891727120](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43891727120).

- `.github/workflows/week47-qo-gated.yml` è stato modificato: il futuro job `experiment` non fa più checkout Git. Un job `package-code`, a valle del preflight, deve fornire **solo quattro file** (runner, preparatore, protocollo, parser canonico) e `prepare-input` fornisce gli snapshot filtrati di entrambe le traslitterazioni.
- Il workflow di smoke `.github/workflows/week47-code-isolation-smoke.yml` ha verificato su un worker separato: **esattamente quattro file, `.git` assente, corpus originali assenti, `HOLDOUT.md` assente, SHA canonici verificati.**
- **Limite:** questa è una prova tecnica dell'architettura; il vero job scientifico non è stato eseguito, né è stato provato un attestato indipendente sul contenuto della policy nascosta.

## 5. Decisione dei gate (nessuna promozione automatica)

`gate.json` è **deliberatamente non modificato** e mantiene `PENDING` in ciascuna voce:

| Gate | Evidenza ora disponibile | Passo ancora necessario |
|---|---|---|
| `partition_policy` | Selettore storico vs W47: MATCH algoritmo e insieme | Revisione esplicita della prova e della catena di provenienza, senza fare affermazioni sull'indipendenza dell'holdout |
| `parser_evidence` | Seconda tokenizzazione: corrispondenza completa a livello di locus, blocco e coppia | Attestazione immutabile delle mappe dettagliate e loro provenienza, con revisione separata |
| `preparer` | Snapshot W47 pin SHA e test contro leakage malformato, CI PASS | Review del contratto di input completo e della scelta degli elementi conservati |
| `runner` | Oracle matematico sintetico PASS | Revisione separata del runner scientifico e coerenza con tutte le soglie del protocollo |
| `input_isolation` | Verifica checkout-free reale PASS del codice | Validazione end-to-end del flusso `preflight→pacchetto codice→snapshot→runner`, senza avviare l'endpoint in assenza di gate |

**Non usare il successo dei test tecnici per approvare automaticamente `gate.json`.** La firma/decisione del revisore indipendente e la prova dell'immutabilità del manifest nel suo insieme sono ancora richieste. In assenza di attestazioni entro venerdì **20/11/2026 ore 18:00 Europe/Rome**, il nuovo esperimento non parte e il rapporto W47 riporta `NOT VERIFIABLE`. La globale `verify.yml` resta FAIL per l'esperimento storico `001` privo di `attempt.yml`; non è stata aggirata.

**Stato finale di questo audit:** `TECHNICAL_EVIDENCE_RECOVERED`; `SCIENTIFIC_GATE_PENDING`. `main`, G0 e RC1.4.2 invariati.
