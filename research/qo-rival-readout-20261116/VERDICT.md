# QO-RIVAL-01 — lettura avversaria dei risultati (2026-11-16)

**Stato quaderno:** CONCLUSO (audit di risultati già eseguiti); **stato scientifico:** ESPLORATIVO / NON VALIDATO. Non è un nuovo tentativo qualificante.

## Provenienza verificata
- Repository: Superb0b0/voynich-entropy-lab
- HEAD sorgente: `research/qo-isolated-replay-20261116` @ `ffb31426f93a288fd6f63f9d3ef677ddbd9e600c`.
- Run originale: https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/43777619545 (SUCCESS, 2026-11-15 23:58–23:59 UTC).
- Artifact risultati: `qo-isolated-results`, ID `14186638018`, SHA-256 ZIP `f2f1c4bc97fa6c8657b4021caaea5c5975427ab04bb9a2c85ba4ebb68426cf24`. Risultati qui trascritti dai **log effettivi della run**, non da un nuovo replay.
- Protocollo congelato `research/qo-rival-protocol.md`, Git blob SHA-1 `906ec20620e324306eba0efc065f8a8700c5bf89`; fonte dichiarata `ZL3b-n.txt` SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`.
- Snapshot di training nella run: SHA-256 `aba161811f3400c6810d43803f7a3ced5243ea29dd862eeb8c9b1ad144a9e38d`.
- Tutto resta training-only. Nessun nuovo accesso al corpus riservato da questo audit; il filtro e l'origine del materiale vanno sottoposti a revisione indipendente.

## Dati dei log (nessuna nuova elaborazione del manoscritto)
Unità dichiarata: transizioni di prima parola in righe P consecutive, all'interno dello stesso paragrafo. Numeratore `qo→qo`: **14**; denominatore: **396**; tasso osservato: **0.03535353535**.

| Confronto | Tasso medio nullo | p unilaterale di deplezione | Correzione Holm (famiglia di 2) |
| --- | ---: | ---: | ---: |
| Shuffle delle prime parole entro paragrafo | 0.1648565976 | 0.0004997501 | 0.0009995002 |
| Shuffle delle prime parole entro folio | 0.1717863588 | 0.0004997501 | 0.0009995002 |
| Circular shift entro ogni paragrafo (diagnostico) | 0.0342889342 | 0.5577211394 | non nella famiglia preregistrata |

Circular shift, 95% simulato [0.0302267003, 0.0367454068]; 2.000 repliche, seed 20261115. Lo shuffle usa 2.000 repliche per modello, seed 20261113. La run ha ripetuto deterministicamente i calcoli due volte sullo stesso input. **Non è una replica indipendente.**

## Interpretazione avversaria
1. Il criterio di morte preregistrato per i **due shuffle** risulta superato sul training: forte scostamento dai due modelli semplici. Questo è l'unico senso legittimo del messaggio automatico `eseguito: confermato` in `tools/qo_isolated_runner.py`.
2. Il **circular shift conserva l'ordine** delle prime parole dentro ciascun paragrafo e, salvo gli effetti di bordo, conserva quindi anche le adiacenze `qo→qo`. Il suo p=0.558 **non falsifica** la deplezione osservata contro gli shuffle, ma mostra che l'osservato non si distingue da un nullo che conserva proprio la struttura locale da spiegare. Non è un generatore rivale indipendente per questo statistico; limita un'eventuale ipotesi sull'ancoraggio ai confini.
3. **Non si può inferire** linguaggio, cifrario, istruzioni, semantica o decifrazione da questi confronti. I null non modellano generatori noti e manca verifica indipendente su folii non usati nella scoperta. Si è usata solo ZL3b; IT2a non costituisce ancora replica in questa run.
4. La CI dedicata SUCCESS prova esecuzione e determinismo per quel workflow, **non** il superamento della CI globale `verify.yml` o la conformità a tutti i gate scientifici.
5. Il parser è semplificato e la policy di esclusione è codificata nel programma; occorre audit indipendente della compatibilità col parser canonico e dell'isolamento, senza pubblicare identificativi o leggere i folii riservati.

## Scelta della pista seguente (senza aprire l'holdout)
- **A.** Riesaminare un terzo shuffle simile: basso valore informativo; modello non distingue il meccanismo e rischia duplicazione.
- **B.** Confronto preregistrato di **generatori meccanici e linguistici calibrati** (es. generatori attestati/controlli negativi), con metrica `qo→qo` e predizioni addizionali non selezionate ex post, split per folio e due trascrizioni quando comparabili. Maggiore potere discriminante ma richiede prima input e SHA-256 dei generatori, parser verificato e registro del protocollo. **Selezionata B; NON ESEGUITA.**

**Verdetto:** `TRAINING_SIGNAL_UNDER_SIMPLE_SHUFFLES; CIRCULAR_SHIFT_NON_DISCRIMINATING; NOT_VALIDATED`. Non promuovere a CONOSCENZA CONFERMATA.

**Prossima azione concreta:** reperire i file e le impronte di generatori rivali già approvati in repository/Library; predisporre solo allora preregistrazione nuova, separata dagli esiti QO-RIVAL-01; mantenere chiuso l'holdout.
