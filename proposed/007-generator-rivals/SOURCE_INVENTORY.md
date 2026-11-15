# Attempt 007 — Inventario delle fonti rivali (ricognizione 2026-11-15)

Stato: SOURCE_DISCOVERY_ONLY; nessun corpus importato nel repository, nessun SHA-256 del contenuto verificato, nessuna esecuzione scientifica.

## 1. Timm–Schinner, self-citation
- Articolo: Timm & Schinner, *A possible generating algorithm of the Voynich manuscript*, Cryptologia (2019/2020), DOI 10.1080/01611194.2019.1596999.
- Sorgente ufficiale: https://github.com/TorstenTimm/SelfCitationTextgenerator
- Materiale verificato tramite GitHub Contents API: `source/` (pom.xml e src), `executable/text-generator.jar` (194341 byte, Git blob SHA-1 7fa14434f896420d6ef626e229f17a453756c9cb), `executable/conf.properties` (Git blob SHA-1 75f44e933ee05b91b95ca6188e54bad636de43f9).
- Licenza del repository: MIT (LICENSE, Git blob SHA-1 6b1bd09317974964cf197605719fc6e33a823d94).
- Config osservata: `method.random=pseudo`, `method.random.pseudo.seed=19`, `text.lines_to_create=1200`, `text.lines_per_page=29`, `text.initial_line` tratta dal Voynich f103v.P.9.
- RISCHIO: seed iniziale da un folio del manoscritto; verificare se viola la separazione TRAIN_ONLY prima di qualsiasi esecuzione. Nessun output di questa fonte acquisito o certificato.

## 2. Markov + self-citation / volvelle
- Sorgente: https://github.com/karolrybak/voynichese
- `corpus/voynich-like-markov.txt`: 1,215,853 byte, Git blob SHA-1 4f431843014ecac80728740de7d03ddf19195e75.
- `corpus/voynich-like-volvelle.txt`: 1,212,530 byte, Git blob SHA-1 3ff0c7bd0657238e93e0e46368c35a2547926c58.
- README corpus: Git blob SHA-1 991e72e72b62376e34f96ab67cafc66e0a0808da.
- Dichiarati dall'autore: 200.000 parole sintetiche per corpus, UTF-8, circa 12 parole per riga; Markov ordine 3 + circa 15% self-citation, volvelle a tre anelli indipendenti.
- RISCHI: linee sintetiche senza attestazione di equivalenza dei paragrafi e folii; training sul Voynich da isolare. Non e' un corpus filtrato indipendentemente per il nostro HOLDOUT. Il blob SHA-1 non sostituisce SHA-256 del file.

## 3. Naibbe
- Sorgente: https://github.com/greshko/naibbe-cipher
- `encrypted/nathist_output_ciphertext.txt`: 217.307 byte, Git blob SHA-1 fb5f1e7509773361ea1acf5b4019efdc83cd17e4.
- `encrypted/nathist_output_ciphertext_respaced.txt`: 216.293 byte, Git blob SHA-1 c95b95507e603ca9a7b0dadba2d13eb314e9b7ea.
- Codice `naibbe.py`: Git blob SHA-1 910b7a99532f4630cb59917f9df3de8e98808598.
- Licenza MIT nel repository (LICENSE Git blob SHA-1 6570cbe139bc3530b7d5f6f73d9aa8bc796950e5).
- RISCHIO: il ciphertext puo' conservare le righe del plaintext anziche' la struttura dei paragrafi Voynich; mapping da verificare prima dell'uso.

## Gate ancora non soddisfatti
1. Acquisizione controllata di file e commit immutabili, SHA-256 su byte acquisiti e attestazione del filtraggio indipendente; Git blob SHA-1 e dimensioni sono solo metadati di scoperta.
2. Verifica della struttura: confini di paragrafo, sequenze di righe e numero di coppie valide; senza mapping verificabile il rivale non puo' essere usato per l'esatto test 005/006.
3. Esclusione di leakage, compresi seed e training che potrebbero contenere pagine riservate.
4. Addendum con metrica, soglia e correzione multipla numeriche congelate prima dell'esecuzione.
5. Verificatore senza accesso a .git, con test negativo per `git show`.

Verdetto: FONTI INDIVIDUATE; INPUTS_NON_ACQUIRED; TEST_007_NOT_RUN. Nessun risultato 007, nessuna validazione scientifica.
