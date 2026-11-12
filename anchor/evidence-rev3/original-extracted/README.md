# Voynich ANCHOR · schema rev3 (DRAFT)

Questa revisione non modifica rev2 né Voynich Research Memory 1.0.0. Non autorizza importazioni o analisi nel ramo RC1.4.2/V7.1, che resta CLOSED_PENDING_VALIDATION.

## Uso

```bash
python -m pip install -r requirements.txt
python tests/test_anchor_schema.py
python validate_anchor.py entry.json
```

`jsonschema` da solo non basta. `rfc3339-validator` è obbligatorio e la guardia verifica i formati `date` e `date-time`, interrompendo la validazione con exit 2 se il controllo è assente. Exit 0 = conforme a schema e controlli semantici, exit 1 = voce rifiutata, exit 2 = errore di ambiente/input. `checked_at` non nullo richiede data e ora RFC3339 con fuso; `execution_date` non nullo richiede data valida.

## Semantica

- `RIPORTATO`: dichiarazione documentata, senza riproduzione necessaria. Stato iniziale `PENDING`.
- `RIPRODOTTO`: esecuzione dichiarata con script, digest, comando, data, output_refs e verification.evidence_refs non vuoti e `recomputed=true`. **Non implica revisione indipendente**: può restare `PENDING` e non richiede reviewer/checked_at finché non si propone PASS.
- `PASS`: solo RIPRODOTTO, con reviewer non vuoto, checked_at valido, evidence_refs e output_refs. I riferimenti restano dichiarativi finché non si verificano i byte.
- `FAIL`: failure.reason non vuoto e failure.evidence_refs non vuoti.
- `NOT_ACQUIRED`: lo schema attuale richiede comunque almeno un source_file con SHA-256 dichiarato. Per dati completamente non acquisiti occorre una voce separata nel registro delle lacune, non inventare hash.

## Limiti espliciti

Il validatore **non apre né ricalcola** gli hash dei file sorgente, degli script o degli output, non verifica l'esistenza dei riferimenti e non certifica la riproducibilità. `canonical_id` deve uguagliare `sha256:<sha256>` e non può duplicarsi all'interno di una voce; digest formalmente corretti ma fittizi restano accettati. Serve un successivo audit dei byte e della provenienza prima di attestare la prova scientifica.

## Test e conservazione

59 test automatici: 19 regressione, 37 nuovi, 3 guardie/CLI. `REV2_SHA256.txt` registra il digest dello schema rev2 originale; il pacchetto rev2 non viene modificato. `SHA256SUMS` identifica i file di questa bozza, non certifica gli originali.
