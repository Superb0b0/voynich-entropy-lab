# W47 | Hardening tecnico dei gate (16 novembre 2026)

**Perimetro:** soltanto robustezza del workflow e del filtro di training, senza nuovo esperimento Voynich. Questo documento non approva il runner, non cambia il protocollo congelato, né prova indipendenza del campione.

## 1. Checkout minimali per guardia e preflight

- Commit `99393440b9f9c4cf67b3e369417da5ae60f07ab6` introdusse checkout sparsi per `guard-tests` e `preflight` con assenza esplicita di `HOLDOUT.md`, `data/ZL3b-n.txt`, `data/IT2a-n.txt` dal *working tree*.
- Una prima modifica generò **chiavi YAML `sparse-checkout` duplicate** e fu rifiutata dal validatore GitHub. L'errore è documentato da [run #43870786867](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43870786867). È stata corretta nel commit `703eef1fb755db17ceaee66b1eb9e5dd27fb7e95`; [run #43870985169](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43870985169) **SUCCESS**.
- In questo run `guard-tests` PASS, `preflight`, `prepare-input`, `experiment` SKIPPED. È prova del workflow tecnico, non del risultato scientifico.
- **Limite esplicito:** il checkout sparso non dimostra l'assenza assoluta dei blob protetti negli oggetti Git del runner. La proibizione vale sul *working tree*; la separazione effettiva della fase scientifica e il controllo della policy di esclusione richiedono ancora attestazione.

## 2. Bug del filtro pagina: rischio eredità del flag d'inclusione

- Nel sorgente `research/week47-qo-decision/training_preflight.py`, `slice_pages` riconosceva solo intestazioni `<folio> <!…`. Una intestazione malformata non riconosciuta poteva far ereditare alle righe successive il precedente flag `included`, con conseguente rischio di filtraggio non corretto.
- Commit `f8503a873279188f5cf016a3d0b810253e1ff781`: ora le intestazioni che assomigliano a folio ma hanno formato non valido causano `RuntimeError`; tutti i loci verificano la corrispondenza con la pagina attiva, sia durante la preparazione sia nella verifica dello snapshot.
- Commit `563f2744b5d6d4f50f6778076a8ffa4909fc8926`: **sei fixture sintetiche**, comprese intestazione malformata, locus incrociato, pagina speciale e pagina non ammessa. Nessuna fixture contiene testo Voynich.
- Commit `2cf0edbc3f6a9ee075f3dfd3e7408869a79bc967`: test sintetici in un job senza corpora originali; il successivo job di preparazione dipende dal successo del test.
- Commit `b0f07c2fc56e6a7064e75ca2f15aa9c021490094`: lo stesso controllo viene incluso anche in `guard-tests` dell'esperimento bloccato.
- [Run W47 guard #43871537009](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43871537009): SUCCESS dei guard-test, **preflight e esperimento SKIPPED**.
- [Run training #43871537048](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43871537048): `synthetic-filter-tests` SUCCESS, `prepare` SUCCESS e `verify` SUCCESS. Non esegue endpoint, permutazioni, O/E o bootstrap scientifici.

## 3. Gate rimasti esplicitamente aperti

`research/week47-qo-decision/gate.json` ha ancora `PENDING` per `parser_evidence`, `preparer`, `partition_policy`, `runner`, `input_isolation`.

- Occorre una prova controllata per ogni hash/commit originale e per i manifest locus/blocco/adiacenze e il registro delle differenze, non un JSON autodescritto come `VERIFIED`.
- L'elenco di esclusioni deriva da codice storico: **policy non attestata indipendentemente**. Nessun ID protetto viene divulgato qui.
- Lo schema di `preflight.py` richiede documentazione di provenienza prima dell'abilitazione. Il workflow dedicato è ancora in una PR draft; nessun trigger manuale del test scientifico è stato usato.
- `verify.yml` globale rimane FAIL per la voce legacy `001` priva di `attempt.yml`, senza modifica o bypass.
- **Cutoff intatto:** 20 novembre 2026, 18:00 Europe/Rome. Se persistono lacune, chiudere `NOT VERIFIABLE`, non cambiare i criteri o avviare prove scientifiche per rispettare la data.

**Classificazione dell'intervento:** `TECHNICAL_HARDENING_PASS`, `SCIENTIFIC_GATE_BLOCKED`.
