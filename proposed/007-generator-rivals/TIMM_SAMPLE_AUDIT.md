# 007 — Ispezione diretta del campione pubblicato Timm–Schinner
Data: 2026-11-15. **Nessun test statistico Voynich eseguito.**

## Identita' e accesso
Repository upstream: https://github.com/TorstenTimm/SelfCitationTextgenerator
Commit upstream fissato: `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`.
File: `executable/generate/generated_text.txt`.
Lettura tramite GitHub connector al commit fissato: 62.795 caratteri restituiti; Git blob SHA-1 `31b5f847097d6c31e210d1ebc23ea9878f456607`. **SHA-256 non calcolato sui byte**, quindi il file non e' ancora ammesso come input verificato.

## Contenuto verificato
- Il campione contiene una sezione commentata `#Properties` e `#Statistics` seguita da righe EVA.
- Parametri dichiarati nel file: `text.lines_to_create=1200`, `text.lines_per_page=29`, `method.random=pseudo`, `method.random.pseudo.seed=19`.
- Il seed iniziale e' esplicitamente una riga del manoscritto: `pchal shal shorchdy okeor okain shedy pchedy qotchedy qotar ol lkar` (f103v.P.9 secondo la configurazione).
- Le statistiche dichiarate sono 1.200 righe, 3.156 token non VMS (30%) e 7.678 token VMS (70%). Questi numeri sono dichiarazioni del generatore, non conteggi indipendenti.
- Non sono presenti marcatori IVTFF di folio e paragrafo nel campione. La lunghezza di pagina configurata NON ricostruisce i veri confini di paragrafo o le adiacenze valide del corpus Voynich.

## Decisione tecnica
`CANDIDATE_DISCOVERED / EXACT_005_006_TEST_INELIGIBLE_AS_IS`.
Il campione non puo' essere introdotto nel test 007 originale senza inventare un mapping di paragrafi, alterando il criterio congelato. Si puo' proporre in futuro un benchmark separato, preregistrato, su righe consecutive sintetiche; **non** chiamarlo replica diretta del test 005/006.

## Integrita' e holdout
La presenza di una riga iniziale presa da f103v non dimostra di per se' leakage nell'holdout, ma il corpus sintetico non e' attestato come derivato esclusivamente da training. Non eseguire contro l'holdout. La lettura del file di output pubblicato non ha aperto i corpus protetti del nostro repository.

## Prossimo controllo
Acquisire bytes in un ambiente autorizzato, SHA-256, analisi della licenza e della struttura di tutti i rivali; verificare se uno conserva veramente paragrafi e folii. Se nessuno lo fa, bloccare il confronto esatto e progettare un benchmark separato senza cambiare retroattivamente 005/006.
