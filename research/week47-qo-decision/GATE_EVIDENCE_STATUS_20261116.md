# W47 evidence and gate status | 16 novembre 2026

**Stato operativo: `BLOCKED_PENDING_EVIDENCE`.** Questa nota registra solo prove tecniche osservate. Non attesta un campione indipendente, non approva un nuovo esperimento e non riqualifica le traslitterazioni dello stesso Voynich come repliche indipendenti.

## Aggiornamenti verificati in questa revisione

1. **Freeze dell'intera approvazione:** `research/week47-qo-decision/preflight.py`, commit `a8cc77246ab02b6ee8b46ea2b55e912f7203bbdf`, richiede che l'ultima modifica del *manifest* `gate.json`, non soltanto dei singoli file referenziati, sia presente in un commit antenato con data non successiva al **20 novembre 2026, 18:00 Europe/Rome**. Compara inoltre il contenuto corrente ai byte dell'ultimo commit del manifest. Test sintetici per approvazione pre/post-cutoff, manifest differente e byte incongruenti: [run guard #43880716585](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43880716585) SUCCESS. **Limite:** il timestamp del commit Git è un marcatore di provenienza debole, non una certificazione temporale esterna.
2. **Filtro fail-closed sulle intestazioni non riconosciute:** `training_preflight.py` nei commit `c2ff7c8550fd0c70eb4f9ac0f1e1256e38b9bba2` ed `e04ef390c579b2cfc736a33dfc39333231948d48`: respinge header simili a pagina (esempio artificiale `<f2x>`) o locus che non rispettano il formato riconosciuto. Gli otto fixture sintetici, la preparazione e la verifica dei due snapshot hanno esito SUCCESS in [run #43881263530](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43881263530).
3. **Immutabilità degli snapshot W47:** commit `831966ef2aea60f9f5a55fd0d20d8f94fb184249` e successivo test `553e1ab10fa98e34ab66805f7a7023398b764e0e`. Derivato W47 ZL3b atteso `aba161811f3400c6810d43803f7a3ced5243ea29dd862eeb8c9b1ad144a9e38d` (3.319 loci P, 28.638 token); IT2a atteso `44891f0545382e51a09a607d1f62b88dbfb34acb44b4ca7db56001d54b0e1bd3` (3.318 P, 27.887 token). Il codice ora rifiuta ogni deriva in SHA dello snapshot: [run #43881484717](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43881484717) SUCCESS per fixture, prepare, verify. Il pin dell'hash **non certifica l'origine della lista di folii esclusi**.
4. **I 13 loci fuori dai blocchi non devono scomparire:** `compare_structural_manifests.py` commit `a813312f9e74453b6804eede064f08b3ef1b06e9`, e fixture commit `62c813d6132e519a7268d5e5cdec742dc2d78683`. I loci con `block_id: null` sono accettati solo se `outside_block: true` e privi di riferimenti di adiacenza; assegnazioni fittizie o next-locus vengono rifiutati. [Run W47 #43881659233](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43881659233) SUCCESS: `guard-tests` eseguiti, `preflight`, `prepare-input`, `experiment` SKIPPED. È una verifica delle regole del comparator, **non** produzione di un manifest completo indipendente.

## Provenienza che NON va confusa

La trascrizione training-only ZL3b del diverso protocollo `COMPAT-014-01-A1` ha SHA-256 `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9` (riportato nel [commento #23 sull'audit A1](https://github.com/Superb0b0/voynich-entropy-lab/issues/23)). Il derivato W47 è `aba16181…`. Anche se i conteggi RC1.2 di 3.319 loci e 28.638 token sono uguali, **SHA differenti non dimostrano né equivalenza né differenza degli insiemi di loci**: è necessario riconciliare identità dei record e preprocessing con un audit appropriato, senza dedurre una comparabilità automatica. La catena A1 usa un preparatore storico che può riferirsi a una funzione `protected()` con lettura di `HOLDOUT.md`; non è stata richiamata qui, né il file `HOLDOUT.md` è stato aperto.

## Stato dei cinque requisiti effettivamente bloccanti

| Requisito | Stato | Evidenza acquisita | Lacuna che impedisce l'approvazione |
|---|---|---|---|
| `parser_evidence` | `PENDING` | RC1.2 fonte SHA `8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5`; verifica aggregata 740 blocchi, 4.130 P, 35.492 token, 6.980 tipi; 13 P fuori blocco | Attestazione indipendente di manifest locus/blocco/adiacenza e mapping IT2a, registri differenze completi e revisionati |
| `preparer` | `PENDING` | Slicer modificato con rifiuto errori, SHA dei due snapshot W47 congelati | Approvazione del codice di preparazione con provenienza e revisione indipendenti |
| `partition_policy` | `PENDING` | Implementazione storica dei folii esclusi in `tools/qo_rival_calibration.py`; nessun contenuto protetto divulgato | Prova indipendente che la policy hard-coded corrisponda alla partizione autorizzata, senza assumere derivati differenti equivalenti |
| `runner` | `PENDING` | Solo test sintetici, nessun endpoint misurato sul Voynich | Revisione indipendente del runner rispetto ai parametri *già* congelati |
| `input_isolation` | `PENDING` | Job `verify` separato senza originali nel working tree, snapshot filtrati verificati per SHA | Attestazione del confine di fiducia, incluso rischio degli oggetti Git e dell'origine della partizione |

## Vincoli rimasti invariati

- L'unica domanda W47 autorizzabile è `NULL_ONLY`, esatta ripetizione della prima parola nelle coppie P consecutive entro blocco IVTFF contro shuffle entro blocco; non un confronto con Timm–Schinner, non la variabile posizionale `qo-`.
- Protocollo congelato commit `69b32db1126c99cb4230b05c7bb33e5292aa6d45`, SHA-256 `22b4a8bc3951f6ccf06aeffffc9e45a016e33847ee51d3fe67f1d35751494f90`, **inalterato**.
- `main` non toccato. [PR #26](https://github.com/Superb0b0/voynich-entropy-lab/pull/26) in bozza. Nessun nuovo test scientifico, O/E, p-value o bootstrap su dati del manoscritto.
- La `verify.yml` globale resta FAIL per legacy 001 senza `attempt.yml`; non modificarla né silenziare quel caso per ottenere un falso verde.
- Se tutti i gate non sono attestati e congelati prima del **20 novembre 2026 alle 18:00** locali, NON eseguire il nuovo test; chiusura `NOT VERIFIABLE` con lacune documentate. Un run di test sintetici verde non autorizza automaticamente la promozione.

**Verdetto di questa revisione:** rafforzamento tecnico PASS; autorizzazione scientifica ancora BLOCCATA. 
