# LOG.md - registro aggiunto il 2026-11-13

Attenzione: nel branch main e in anchor-rev3-staging-20261112 non erano presenti LOG.md, KNOWLEDGE.md, STATE.md, attempts/ al momento dell'avvio. Questo registro nasce oggi: non è ricostruzione completa dei lavori storici.

- 2026-11-13 | 001-paragraph-header-key | ESPLORATIVO, H1 NON SOSTENUTA | Split 0 p=0,746 e split 1 p=0,002, disaccordo. Prove e codice in attempts/001-paragraph-header-key/. Gate RC1.4.2 invariato.

- 2026-11-13 | 002-currier-header-interaction | ESPLORATIVO, H2 NON SOSTENUTA | Contrasto A/B p=0,539 e p=0,131. Non qualifica ancora come ciclo completo secondo il successivo PROTOCOL.md v1 (calibrazione e confondenti non eseguiti). Evidenze in attempts/002-currier-header-interaction/.

- 2026-11-13 | 003 first-word exact-repeat | training folio split O/E 0.461, 0.673; p 0.01798, 0.17782; NOT SUPPORTED.
- 2026-11-13 | 004 qo->qo | training folio split O/E 0.246, 0.131; p 0.000999 each; exploratory training signal only. Holdout untouched.
## 2026-11-14 - attempts 005 e 006
Precursore esplorativo (non archiviato come attempt): modello refrattario di classe (solo theta) tarato su uno split e predetto sull'altro, ZL3b training-only: totale adiacenze di stessa classe e ripetizioni esatte previste correttamente, qo->qo sovrastimato di circa 3 volte in entrambe le direzioni (osservato 2 vs 3-12; 12 vs 19-37). Da qui il parametro phi. Attempt 005 (ZL3b): SUPPORTED per il criterio di contenimento fissato; attempt 006 (IT2a, stesso codice): NOT SUPPORTED per un solo conteggio (128 vs intervallo 93-127). Replay locale con tools/verify_attempts.py::verify_attempt e isolamento strace: PASS per 005 e 006. CI GitHub non eseguita. Holdout non aperto.

## 2026-11-20 — Provenienza del replay 005 e 006

Il [replay del 17 novembre](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/44121429725) ha riprodotto i risultati archiviati sul training con tolleranza `1e-6`. Il 20 novembre l’elenco degli artefatti del [run sorgente](https://github.com/Superb0b0/voynich-entropy-lab/actions/runs/44110677734) risulta vuoto. La causa della scomparsa del bundle è indeterminata.

Per rigenerare gli input, il custode può usare il job `prepare-training-data` con i corpus canonici, il manifest HMAC e il segreto dell’ambiente `holdout-custodian`. Il comando è `python tools/prepare_training_data.py --output-dir "${RUNNER_TEMP}/training-only"`. La procedura produce due corpus filtrati e `training_manifest.json`. [Procedura versionata](https://github.com/Superb0b0/voynich-entropy-lab/blob/2e1fc980263cd7793f82a775e84228f0d5f01d98/.github/workflows/verify.yml) · [Script di preparazione](https://github.com/Superb0b0/voynich-entropy-lab/blob/2e1fc980263cd7793f82a775e84228f0d5f01d98/tools/prepare_training_data.py)

| File rigenerato | SHA-256 atteso |
|---|---|
| ZL3b-n.txt | `dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9` |
| IT2a-n.txt | `a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c` |

Prima del replay, il verificatore controlla queste impronte, il manifest e l’esclusione di 48 blocchi per corpus. Il workflow storico documenta i checkout isolati e il commit del verificatore. Per una nuova esecuzione occorre fornire il bundle rigenerato al posto dell’artefatto storico. La rigenerazione resta da eseguire. [Controlli sugli input](https://github.com/Superb0b0/voynich-entropy-lab/blob/2e1fc980263cd7793f82a775e84228f0d5f01d98/tools/verify_selected_training_attempts.py) · [Replay storico](https://github.com/Superb0b0/voynich-entropy-lab/blob/2e1fc980263cd7793f82a775e84228f0d5f01d98/.github/workflows/verify-005-006.yml)

La [revisione della PR #9](https://github.com/Superb0b0/voynich-entropy-lab/pull/9#pullrequestreview-5993910020) è un’autorevisione registrata come `COMMENTED` da `Superb0b0`, autore della PR. La verifica indipendente resta aperta. I verdetti scientifici sono esplorativi, 005 `SUPPORTED` su ZL3b e 006 `NOT SUPPORTED` su IT2a.
