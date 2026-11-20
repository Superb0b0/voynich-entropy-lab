# W47 | Rapporto tecnico di sblocco parziale (2026-11-16)

**Natura:** audit strutturale e CI preventiva, **NESSUN ESPERIMENTO SCIENTIFICO ESEGUITO**. Nessun utilizzo dei dati protetti per stimare un modello, nessun nuovo valore O/E. Il quesito resta `NULL_ONLY`: ripetizione esatta della prima parola contro permutazione entro blocco IVTFF; Timm–Schinner non attestato/non incluso.

## Baseline e parser
- G0 #23 CHIUSO CON ESCLUSIONI; canonical ZL3b SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; parser RC1.2 SHA-256 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`.
- Replay locale indipendente dal codice EXP-SEQ-05 storico: **4130 loci P, 35492 token, 6980 tipi**, differenze nei token puliti **0/4130**. **740** aperture `<%>` e **740** chiusure `<$>`, appaiate senza annidamenti, attraversamenti di pagina o blocchi orfani. **4117 loci P** in blocchi delimitati, **13** fuori; l'effetto può riguardare soltanto una popolazione esplicitamente inclusa.
- Lo schema di adiacenza richiede linee P fisicamente contigue e indice locus consecutivo: non confondere semplice incremento numerico e adiacenza fisica; la lista eleggibile deve essere definita prima di qualsiasi analisi.
- Script audit pubblicato in `research/week47-qo-decision/structural_audit.py`, origine `1cbcc9a4b38c5bf294e5f2c1f348e4158eb4bbc0`; workflow solo lettura `.github/workflows/week47-structural-audit.yml`. [Run di controllo rigoroso #43866535563](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866535563): **SUCCESS**, senza endpoint `qo-`.
- Comparabilità intertrascrizione dell'intero corpus **NON IDENTICA**: IT2a contiene **4118 loci P e 772 blocchi**; corrispondono per ID e confini **672 blocchi**, con **0 differenze Currier A/B** nei blocchi comuni; coppie fisicamente contigue presenti *nello stesso blocco* in entrambe le trascrizioni **2897**. Restano 68 blocchi solo ZL3b, 100 solo IT2a; la popolazione completa NON può essere trattata come comune.

## Isolamento training-only e prova della geometria comune
- `training_preflight.py` filtra **entrambe** le trascrizioni per intestazioni di pagina e politica di esclusione già definita, senza esporre i folii riservati; le unità speciali non numeriche sono escluse e dichiarate come classe. 
- Workflow `.github/workflows/week47-training-preflight.yml`: job `prepare` controlla SHA-256 degli originali e produce i due soli snapshot di training; job `verify` fa sparse checkout del codice e scarica **solo** gli snapshot di training, senza `HOLDOUT.md` o corpus originali. [Run #43867293834](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43867293834): **prepare SUCCESS, verify SUCCESS**, prova di assenza dei file protetti nel job `verify` PASS.
- SHA-256 training ZL3b `aba161811f3400c6810d43803f7a3ced5243ea29dd862eeb8c9b1ad144a9e38d`: **3319 loci P, 28638 token, 601 blocchi**.
- SHA-256 training IT2a `44891f0545382e51a09a607d1f62b88dbfb34acb44b4ca7db56001d54b0e1bd3`: **3318 loci P, 27887 token, 628 blocchi**.
- Nei due snapshot: **548 blocchi comuni** per ID/confini, **548** con stessa attribuzione Currier; **521 blocchi A/B** con stessa lista di loci P e medesimo grafo di coppie; **2241 coppie** esattamente corrispondenti, su **75 folii fisici** con blocchi allineati. Queste sono quantità strutturali, **non** risultati scientifici.
- L'indipendenza epistemica NON deriva dalla separazione dei job né dalla seconda traslitterazione.

## Runner futuro: solo test sintetici
- `research/week47-qo-decision/run_locked.py` è implementato, ma **NON approvato** sul manifest `gate.json`. Usa SHA-256 di parser/protocollo frozen, soltanto snapshot isolati, il medesimo sottoinsieme A/B con geometria comune, 10.000 shuffle e 10.000 bootstrap per folio, soglie prespecificate e doppio replay byte-identico. Nessun dato grezzo, token, ID di folio o lista di selezione viene scritto nel risultato. 
- `tests/test_week47_locked_runner.py` contiene soltanto fixture artificiali: ripetizione invariabile, depletion sintetica, p-value, seed, IC, casi impossibili, minimo folii, classificatore.
- [Run workflow gate #43868943140](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43868943140): **guard-tests SUCCESS**; `preflight`, `prepare_training` ed `experiment` **SKIPPED**. Non usare il verde come attestato di scientificità. La connessione tra preflight, preparatore di training e runner è stata cablata sul ramo draft senza esecuzione scientifica.
- `gate.json` resta volontariamente `PARSER_EVIDENCE=PENDING`, `RUNNER=PENDING`, `INPUT_ISOLATION=PENDING`; non falsificare attestazioni e non far partire l'esperimento finché non esiste review indipendente della provenienza e dell'isolamento. La precedente verifica globale `verify.yml` fallisce per il legacy 001 privo di `attempt.yml`; nessun bypass.

## Decisione e resto del perimetro
- **PASS tecnico strutturale ZL3b:** sì; **PASS di un audit isolato training-only su due traslitterazioni:** sì; **APPROVAZIONE SCIENTIFICA DI ESECUZIONE:** no.
- Entro **venerdì 20 novembre 2026 alle 18:00 Europe/Rome** servono attestazione bloccante del parser/adiacenza e del mapping, contratto/runner verificati e manifest completo con commit antecedenti. In assenza di uno solo di essi, `NOT VERIFIABLE` è la conclusione corretta. Non spostare la scadenza, cambiare endpoint o utilizzare un rivale non attestato.
- `main`, G0, RC1.4.2 e baseline pubblica non sono stati modificati; tutti i commit qui citati appartengono a [PR #26, DRAFT](https://github.com/Superb0b0/voynich-entropy-lab/pull/26).

**Questa registrazione è una fotografia tecnica, non una predizione o scoperta sul significato del Voynich.**


## Addendum 17 Nov 2026 — revisione tecnica e gate W47

**Perimetro e interpretazione statistica.** La revisione avversariale ricevuta sul codice redatto è un controllo tecnico parziale, non un'attestazione indipendente né una validazione scientifica. La policy `HELD` e l'identità della versione originale restano **NOT VERIFIABLE**. Il risultato previsto dal protocollo congelato può essere descritto soltanto come **deviazione dal nullo di permutazione entro blocco IVTFF**. Non dimostra evitamento tra righe consecutive. Effetti posizionali `qo-` sono già noti nel corpus; pertanto un O/E basso è plausibile anche senza un effetto aggiuntivo di evitamento e un eventuale **SUPPORTED** avrebbe peso informativo limitato. Questa è una limitazione interpretativa da riportare, non un cambiamento di endpoint o del nullo congelato.

**Rafforzamento del gate pubblicato su PR #26.** I commit `e8e8c2ba25681d43a05d814bb1404a354950599a`, `3088eb37e57c0c597022702b817016b1a9940dc5`, `d5eb0b9e86025865446cc14bb8907fb9498a50a3`, `e9162c47e39799726c73de3478fc02d4a87031c8`, `af109783aa715b25eb0f078da8f0356e91ded6bd`, `c4dde05d1e3cb7a15b01576db96c6a696079f316`, `e45471e337ca8952de33e25db65079d2f3c05b70` e `151e5391ae53ea41d7b933c3a042bb0c460a007d` rimuovono la data del committer come autorità temporale, richiedono una review GitHub `APPROVED` non dell'autore sul commit esatto e legano l'avvio del runner alla ricevuta preflight dello stesso run GitHub e ai relativi job riusciti. Il gate `gate.json` resta privo delle attestazioni commit/hash: la revisione del codice non compila né approva quelle prove.

**Verifiche tecniche sul commit `151e5391ae53ea41d7b933c3a042bb0c460a007d`.** Le cinque suite artificiali nel workspace sono PASS (59 test totali) e `py_compile` è PASS. In Actions: `W47 qo null-only gated experiment` #44063040763 PASS, `W47 checkout-free isolation smoke` #44063040807 PASS, `W47 independent parser parity` #44063040894 PASS, `W47 structural parser audit` #44063040864 PASS, `W47 training-only alignment preflight` #44063040796 PASS, `W47 policy provenance` #44063040691 PASS e `W47 independent synthetic runner oracle` #44063040753 PASS. Nel gate workflow, `preflight`, `prepare-input`, `package-code` ed `experiment` sono tutti **SKIPPED**; nessun dispatch manuale o esperimento è stato eseguito. Il workflow globale `Verify archived attempts` #44063040731 resta FAIL per il tentativo legacy `001` privo di `attempt.yml`; non è stato aggirato né silenziato.

**Esito operativo:** le correzioni tecniche dei punti 1–3 sono presenti, ma la loro attestazione al gate resta **NOT VERIFIABLE** finché il manifest non registra prove congelate e una review valida. Restano fuori dal codice e non verificati i ruleset di branch, CODEOWNERS e un Environment con revisori. **SCIENTIFIC_RUN_BLOCKED.** Il protocollo, le baseline e i dati protetti non sono stati modificati o usati.


**Controllo amministrativo read-only (17 Nov).** La collection GitHub repository rulesets ha restituito `[]`. `CODEOWNERS` non esiste nei percorsi riconosciuti `/CODEOWNERS`, `.github/CODEOWNERS` e `docs/CODEOWNERS` (404). La lettura della protezione specifica del branch non è riuscita tramite l'endpoint disponibile; l'enumerazione degli Environments è fuori dai permessi dell'integrazione. Quindi ruleset e CODEOWNERS risultano assenti, mentre branch protection ed Environment restano **NOT VERIFIABLE**.


## Addendum 17 Nov 2026 — Environment e follow-up review

- Il workflow ora assegna il job `experiment` all'Environment GitHub `w47-science` (commit `c1886b80c0081fd5403e6b6c9df227c917a244fd`) e il test sintetico controlla che il vincolo resti presente. La configurazione di revisori/branch restriction dell'Environment non è impostabile o verificabile tramite l'integrazione disponibile: la sola dichiarazione nel workflow non costituisce una protezione.
- Sul commit `95b5b07f4ca0f884aca7b331e78ac6c02dcf6976`: W47 gate #44073651097, isolamento #44073651441, parità #44073651076, audit strutturale #44073651162, preflight training #44073651016, policy #44073651176 e oracolo sintetico #44073651003 sono PASS. Il workflow gate ha saltato preflight/preparazione/esperimento; `Verify archived attempts` #44073651004 resta FAIL per il legacy 001 senza `attempt.yml`.
- La menzione `@claude` è stata pubblicata sul diff. La richiesta formale di reviewer GitHub è stata respinta con HTTP 422 perché l'utente `claude` non è collaborator. Non risulta una review formale del nuovo head; serve un reviewer collaboratore indipendente.

Lo stato scientifico resta **SCIENTIFIC_RUN_BLOCKED**. Nessun dato protetto o protocollo congelato è stato usato o modificato.


## Addendum 17 Nov 2026 — verifica del ruleset creato

La precedente osservazione “ruleset assente” era corretta alla verifica iniziale, ma è superata dalla successiva creazione. Lettura API del ruleset attivo **protect-main-for-holdout-gate**, ID `27456310`, effettuata dopo la creazione:

- target: solo branch predefinito (`~DEFAULT_BRANCH`), quindi **non** il branch W47 `research/week47-qo-rivals-plan-20261116`;
- regole attive: divieto di cancellazione e force-push, PR obbligatoria, una review approvante;
- bypass vuoto, `current_user_can_bypass=never`;
- nessun required status check, Code Owner review disattivata, stale reviews non dismissate;
- `CODEOWNERS` assente; la protezione dell'Environment `w47-science` tramite reviewer resta non verificata.

Il ruleset migliora la protezione di `main`, ma non chiude il rischio del dispatch dal branch W47. La review esatta non autore rimane anche imposta dal preflight; nessuna review formale del head corrente è attestata. **SCIENTIFIC_RUN_BLOCKED**.
