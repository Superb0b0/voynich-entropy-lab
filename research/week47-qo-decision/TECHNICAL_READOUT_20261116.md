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
