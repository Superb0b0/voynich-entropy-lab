# LOG.md - registro aggiunto il 2026-11-13

Attenzione: nel branch main e in anchor-rev3-staging-20261112 non erano presenti LOG.md, KNOWLEDGE.md, STATE.md, attempts/ al momento dell'avvio. Questo registro nasce oggi: non è ricostruzione completa dei lavori storici.

- 2026-11-13 | 001-paragraph-header-key | ESPLORATIVO, H1 NON SOSTENUTA | Split 0 p=0,746 e split 1 p=0,002, disaccordo. Prove e codice in attempts/001-paragraph-header-key/. Gate RC1.4.2 invariato.

- 2026-11-13 | 002-currier-header-interaction | ESPLORATIVO, H2 NON SOSTENUTA | Contrasto A/B p=0,539 e p=0,131. Non qualifica ancora come ciclo completo secondo il successivo PROTOCOL.md v1 (calibrazione e confondenti non eseguiti). Evidenze in attempts/002-currier-header-interaction/.

- 2026-11-13 | 003 first-word exact-repeat | training folio split O/E 0.461, 0.673; p 0.01798, 0.17782; NOT SUPPORTED.
- 2026-11-13 | 004 qo->qo | training folio split O/E 0.246, 0.131; p 0.000999 each; exploratory training signal only. Holdout untouched.
## 2026-11-14 - attempts 005 e 006
Precursore esplorativo (non archiviato come attempt): modello refrattario di classe (solo theta) tarato su uno split e predetto sull'altro, ZL3b training-only: totale adiacenze di stessa classe e ripetizioni esatte previste correttamente, qo->qo sovrastimato di circa 3 volte in entrambe le direzioni (osservato 2 vs 3-12; 12 vs 19-37). Da qui il parametro phi. Attempt 005 (ZL3b): SUPPORTED per il criterio di contenimento fissato; attempt 006 (IT2a, stesso codice): NOT SUPPORTED per un solo conteggio (128 vs intervallo 93-127). Replay locale con tools/verify_attempts.py::verify_attempt e isolamento strace: PASS per 005 e 006. CI GitHub non eseguita. Holdout non aperto.
