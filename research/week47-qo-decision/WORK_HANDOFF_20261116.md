# Work handoff | W47 Voynich | 16 novembre 2026

**Destinazione:** riprendere operativamente dal draft [PR #26](https://github.com/Superb0b0/voynich-entropy-lab/pull/26), branch `research/week47-qo-rivals-plan-20261116`. Non è un'autorizzazione a lanciare il test scientifico.

## Gate obbligatori

Prima di agire, leggere per intero gli issue [#22](https://github.com/Superb0b0/voynich-entropy-lab/issues/22) e [#23](https://github.com/Superb0b0/voynich-entropy-lab/issues/23), **inclusi i commenti**. In #23 sono presenti addenda COMPAT-014 distinti da W47; non confonderli.

- G0 `CHIUSO CON ESCLUSIONI`; corpus canonico ZL3b SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.
- Parser RC1.2 SHA-256 `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`; 740 blocchi marcati, 4.130 loci P, 35.492 token, 6.980 tipi (non forzare conteggi di un derivato training a questi totali globali).
- Unica domanda W47 `NULL_ONLY`: ripetizione esatta della prima parola in coppie P fisicamente consecutive, nello stesso blocco IVTFF, contro permutazione **entro blocco**. Non paragonare a Timm–Schinner senza altra attestazione né promuovere QO-MECH-01 a effetto posizionale comparabile.
- Protocollo W47 **immutabile** in `research/week47-qo-decision/PROTOCOL.json`, commit `69b32db1126c99cb4230b05c7bb33e5292aa6d45`, SHA-256 `22b4a8bc3951f6ccf06aeffffc9e45a016e33847ee51d3fe67f1d35751494f90`.
- Cutoff verifiche: venerdì 20 novembre 2026 ore 18:00 Europe/Rome. Evidenze mancanti => `NOT VERIFIABLE`, nessun nuovo test; il protocollo è esplorativo anche con gate superati.

## Evidenza tecnica disponibile

- [Audit strutturale](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43866535563): ZL3b 740 blocchi; IT2a 772; 672 blocchi comuni, 2.897 coppie comuni in blocchi identici. Le traslitterazioni NON sono identiche, sono lo stesso manoscritto.
- [Isolamento training per entrambe](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43867293834): job prepare e verify SUCCESS, in verify assenti originali e HOLDOUT.md. Training: 521 blocchi A/B con geometria identica, 2.241 coppie allineate e 75 folii fisici rappresentati. **Non** equivale a attestazione indipendente della policy di esclusione.
- `research/week47-qo-decision/run_locked.py`: runner implementato ma **NON AUTORIZZATO** né eseguito su dati Voynich.
- `research/week47-qo-decision/preflight.py`: controllo fail-closed di protocollo, parser, runner e ora anche provenienza **del preparatore training e della policy di esclusione**. `gate.json` mantiene `PENDING` per parser, preparer, partition_policy, runner, input_isolation.
- `.github/workflows/week47-qo-gated.yml`: guard-tests -> preflight -> un SOLO job prepare-input -> experiment (se autorizzato e richiesto manualmente). Mai eseguire il runner con checkout integrale. Nel branch draft soltanto.
- [CI guard dopo nuovo controllo di provenienza](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43869463825): SUCCESS guard-tests; preflight, prepare-input ed experiment SKIPPED. Sono test tecnici, non risultati scientifici.
- `verify.yml` generale è ancora FAIL per legacy 001 privo di `attempt.yml`. Non inventare un contratto e non saltarlo in silenzio.

## Prossimi passi a PRIORITÀ

1. Riesaminare code review e CI del ramo PR #26, tenendo conto di eventuali commit concorrenti e usando blob SHA per aggiornamenti: non sovrascrivere lavoro altrui.
2. Produrre audit indipendente **di un file di prova parser e del mapping** con differenze dettagliate dove necessario, senza alterare il parser originale né esportare dati riservati.
3. Verificare origine dell'elenco di esclusione, hash del preparatore e input-isolation attestation; non basta dichiarare `VERIFIED` in un JSON.
4. Rieseguire solo controlli sintetici e di isolamento finché tutti i requisiti fail-closed non passano. Non modificare mai l'endpoint/soglia congelati alla luce dei risultati.
5. Solo dopo attestazioni autentiche, proporre una decisione sull'eventuale esperimento; altrimenti chiudere `NOT VERIFIABLE` entro scadenza.

**Non toccare main, HOLDOUT.md, baseline o protocolli canonici; RC1.4.2 resta CLOSED_PENDING_VALIDATION.**
