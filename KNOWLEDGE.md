# KNOWLEDGE.md - indice locale delle evidenze

Nota sulla provenienza: creato il 2026-11-13 perché assente dai due branch indicati; gli esperimenti storici non sono qui riclassificati o riscritti.

## 001 - chiave lessicale di apertura del paragrafo
- [FATTO VERIFICATO] Codice eseguito su corpus ZL3b-n.txt e parser RC1.2 con SHA-256 verificati.
- [ESPLORATIVO] La prima riga del paragrafo NON dimostra una capacità di indicizzazione lessicale stabile sul corpo distante: il segnale è presente in un solo split di folii.
- [IPOTESI] L'eterogeneità di currier/mani/fascicoli richiede test autonomo, senza usare questo split come criterio di selezione.
- [LIMITE] Trascrizione IT2a verificata come file in Library ma non processata nel tentativo; nessuna convalida indipendente.
- [DIVIETO] Non inferire traduzione, intenzioni del creatore o meccanismo cifrante da questo tentativo.

## 002 - interazione Currier A/B
- [FATTO VERIFICATO] 155 folii A/B eleggibili; tre esclusi per assenza di etichetta $L=A/B nella testata usata.
- [ESPLORATIVO] Interazione Currier A/B non confermata, p=0,539 e 0,131, due split per folio. Non selezionare a posteriori lo split del 001.
- [LIMITE] Non sono state eseguite calibrazione su generatori noti, correzione confondenti o trascrizione indipendente IT2a. Non contare come nuovo test qualificante per PROTOCOL.md v1.

## 003–004 training-only comparison (2026-11-13)
- [EXPLORATORY] Exact first-word repetition depletion fails two-split criterion.
- [EXPLORATORY] qo->qo avoidance survives within-paragraph shuffling in two training folio splits, including page-shuffle and long-line controls; previous whole-corpus discovery means no independent validation.
- [LIMIT] Rivals ms408/pykeedy not run; parser is simplified, not validated RC1.2. No translation inference.
## 2026-11-14 (ESPLORATIVO, NON VERIFICATO)
- Sul training di ZL3b, dentro il paragrafo, le prime parole di righe consecutive evitano la stessa classe di prefisso: le adiacenze di stessa classe sono circa meta' di quelle attese (342 attese vs 175 osservate nello split 0; 217 vs 128 nello split 1; rivale = rimescolamento dentro il paragrafo). Un solo parametro (theta circa 0,7-0,9, stabile fra split e fra ZL3b e IT2a) predice sull'altro split il totale delle adiacenze non-qo e le ripetizioni esatte della prima parola: l'evitamento della ripetizione esatta e' compatibile con una regola di classe, senza regola per parola.
- qo->qo e' soppresso piu' di quanto preveda la regola generica (osservato circa 0,3-0,4 della previsione solo-theta). Un parametro in piu' (phi circa 1,0-1,7) lo cattura, ma con pochi conteggi (2 e 12) e phi poco stabile fra split; potenza bassa.
- Limiti: classi per prefisso arbitrarie, ordine scambiabile nel paragrafo, nessun confronto con Timm-Schinner ne' calibrazione su generatore noto; IT2a non e' dato indipendente sul testo.
ESPLORATIVO, NON VERIFICATO. Su ZL3b training, dentro il paragrafo e a parita' di lunghezza, nessun legame rilevabile fra ripetizione della classe della prima parola e riuso lessicale del corpo (segni opposti nei due split). Non esclude un legame modesto; non e' una scoperta indipendente per il riuso (misurato sul corpus completo).
