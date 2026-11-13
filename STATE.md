# STATE.md - stato operativo al 2026-11-13

- Ultimo tentativo completato: 001-paragraph-header-key.
- Verdetto: H1 NON SOSTENUTA (ESPLORATIVO). Dati, codice, risultati e criteri in attempts/001-paragraph-header-key/.
- Prossima pista proposta: eterogeneità prespecificata per Currier A/B, mano e fascicolo, mantenendo split per folio; evitare selezione retroattiva in base al test 001.
- Corpus lock: ZL3b-n.txt SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc; parser SHA-256 8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5.
- Stato RC1.4.2: CLOSED_PENDING_VALIDATION; non eseguiti builder, PCA, clustering, coupling.
- Branch anchor-rev3-staging-20261112: preservato, nessuna mutazione.
- Discrepanza iniziale: LOG.md, KNOWLEDGE.md, STATE.md e attempts/ assenti nel main e nello staging all'avvio; aggiunti ora solo a main. Repo xenoglyph-ai/voynich-public consultato in sola lettura.
- Continuità: questa sessione esegue cicli sincroni; automazione ricorrente separata necessaria per ulteriori riprese, non equivale a processo infinito.

## Batch protocol bootstrap — 2026-11-13
PROTOCOL.md committed on main. Current run BLOCKED before five qualifying scientific cycles: full SHA-256 verification of both corpora, prior attempts inventory and user-selected holdout provenance not completed; no new experiment counted. HOLDOUT.md intentionally not created. Next action: inspect full attempts/ and CI, verify complete input hashes and execute folio-split generator-rival tests on training only. Do not claim batch completed.
