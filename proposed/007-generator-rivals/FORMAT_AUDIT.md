# 007 — Audit formato degli altri generatori (2026-11-15)
Stato: ricognizione verificabile, **non** esecuzione dell'esperimento.

## Naibbe
Fonte upstream: https://github.com/greshko/naibbe-cipher
File `encrypted/nathist_output_ciphertext.txt`: 217307 caratteri restituiti, blob Git SHA-1 `fb5f1e7509773361ea1acf5b4019efdc83cd17e4`. 1641 segmenti separati da newline (incluso ultimo eventuale vuoto); 224 occorrenze di righe vuote consecutive.
File `encrypted/nathist_output_ciphertext_respaced.txt`: 216293 caratteri restituiti, blob Git SHA-1 `c95b95507e603ca9a7b0dadba2d13eb314e9b7ea`. Stesso numero di segmenti e righe vuote consecutive.
Entrambi sono stati letti tramite GitHub connector. **Non** contengono marcatori IVTFF di pagina/paragrafo. Le righe vuote potrebbero rappresentare separatori, ma NON e' stato verificato che corrispondano ai paragrafi del Voynich o che il processo di generazione mantenga la struttura originaria. Per questo NON sono ammessi come sostituti diretti delle unita' 005/006.
Non e' stato calcolato SHA-256 sui byte originali; le dimensioni riportate qui sono caratteri restituiti dal connettore e non costituiscono hash di integrita'.

## Markov + volvelle
Fonte upstream: https://github.com/karolrybak/voynichese
GitHub Contents API ha fornito i metadati:
- `corpus/voynich-like-markov.txt`: 1215853 byte, Git blob SHA-1 `4f431843014ecac80728740de7d03ddf19195e75`.
- `corpus/voynich-like-volvelle.txt`: 1212530 byte, Git blob SHA-1 `3ff0c7bd0657238e93e0e46368c35a2547926c58`.
La lettura testuale tramite `fetch_file` ha restituito stringa vuota per entrambi: **contenuto NON ACQUISITO**, non equivale a file vuoti. Non attribuire numero di righe, marcatori o contenuto sulla base di questa chiamata.
Il README del corpus dichiara parole EVA sintetiche separate da spazi e circa 12 parole per riga, senza attestare mapping dei paragrafi reali.

## Decisione
I campioni Naibbe e Timm disponibili non possiedono i marcatori IVTFF necessari per un confronto diretto 005/006; Markov/volvelle richiedono ancora acquisizione dei byte. Non creare pseudo-paragrafi artificiali e non trasformare un test sulle righe in una replica dei test su paragrafi.
NEXT: acquisizione byte con SHA-256 e provenance, ispezione della generazione Naibbe, progettazione separata di benchmark lineare con criteri congelati, test negativo del bypass `.git`.
HOLDOUT non aperto, 007 non eseguito, RC1.4.2 CLOSED_PENDING_VALIDATION.
