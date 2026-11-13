# CI di riproducibilità — EXP_SEQ_LINE_MEMORY_01

Kit autonomo, in italiano, preparato il 13 novembre 2026. Esegue soltanto l'esperimento storico `exp_line_memory.py` su copie temporanee degli input e confronta l'output con i risultati archiviati. Non esegue builder RC1.4.2, PCA, clustering o conditional coupling. Non modifica il gate `CLOSED_PENDING_VALIDATION`.

## Contenuto e provenienza

Fonte: `VOYNICH_SEQ_LINE_MEMORY_20261112.zip` nella Library.
SHA-256 ZIP originale: `102cf338310aa797103729c8774dc7c41861710409b4016709a4c6f0b4db60ea`.
Tutti i 30 digest del suo `SHA256SUMS.txt` sono stati confrontati con i byte contenuti: 30 OK, 0 diversi.

- `experiment/exp_line_memory.py`: script originale invariato.
- `experiment/inputs/`: corpus ZL3b, tabella P e parser RC1.2 originali invariati.
- `expected/`: `results.json` e `permutation_distributions.csv` originali, usati come baseline immutabile.
- `ci/integrity.json`: digest e dimensioni dei sette file vincolati (script, tre input, due risultati attesi, requirements).
- `ci/verify.py`: verifica degli hash, esecuzione isolata e confronto.
- `.github/workflows/line-memory.yml`: workflow manuale, da installare con l'intero contenuto del kit alla radice di un checkout dedicato.
- `validation-local/`: evidenze dell'esecuzione locale; non sono un esito di GitHub Actions.

Il kit seleziona un solo esperimento. Non esegue tutti gli script dello ZIP e non include una nuova analisi IT2a. Il file IT2a originale è comunque stato trovato nel pacchetto sorgente e il suo digest coincide con `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`.

## Ambiente fissato

Python **3.12.14**, NumPy **2.3.5**. Lo script selezionato usa NumPy e moduli della libreria standard; SciPy, scikit-learn e matplotlib, presenti nel requirements generale del dossier, non servono a questo esperimento.

Le versioni scelte sono quelle disponibili e controllate in questa sessione; la versione NumPy dell’esecuzione storica non è documentata nel results.json archiviato. Il workflow richiede Ubuntu 24.04 e le versioni sopra. Il sistema operativo del runner e le action sono fissati per versione principale, non per immagine/digest o commit: il kit non pretende la riproduzione bit per bit dell'intero ambiente. La prima prova locale usa il runtime disponibile, con versioni Python e NumPy controllate; non è una prova su un runner GitHub pulito.

## Esecuzione

Dalla radice del kit:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --only-binary=:all: -r requirements-ci.txt
python ci/verify.py --check-only
python ci/verify.py
```

Il comando completo scrive in `ci-output/`, lancia lo script originale da una directory temporanea e non sovrascrive la baseline. Per un output separato: `python ci/verify.py --output /percorso/nuovo`.

In GitHub: estrarre l'intero kit alla radice di un checkout dedicato, conservarne gli input, committare e avviare manualmente **LINE_MEMORY - reproducibility**. Il workflow non parte su push e ha permessi `contents: read`; conserva l'esito e il log come artifact. Installazione, commit e avvio GitHub non sono effettuati da questo kit.

## Criteri di confronto fissati prima della lettura dell'output locale

- Hash e dimensioni di script, input e baseline: uguaglianza esatta; mismatch significa errore.
- JSON: stesse chiavi, tipi e lunghezze; interi, stringhe e booleani esatti. Float finiti con tolleranza assoluta e relativa `1e-12`.
- CSV: stesso numero di righe/colonne e stesse celle testuali; i valori archiviati sono già arrotondati a otto decimali.
- Identità byte per byte di entrambi gli output: registrata separatamente nel report, senza confonderla con il confronto numerico.
- Input e script della copia temporanea: ricontrollati dopo l'esecuzione. Gli originali vincolati: ricontrollati a confronto concluso.

Il seme resta `20261112`; permutazioni `1999`; bootstrap per folio `2499`. Nessun aggiustamento degli attesi ai nuovi risultati.

## Perimetro scientifico

Status invariato: **ESPLORATIVO**. Un confronto PASS attesta la riproducibilità dell'output archiviato nel perimetro dichiarato, non la correttezza dell'ipotesi, una decifrazione, una preregistrazione retroattiva o la chiusura del gate RC1.4.2/V7.1.

Le 207 unità folio e le 4.130 righe P appartengono all'esperimento LINE_MEMORY e al suo parser RC1.2: non sostituiscono la popolazione primaria RC1.4.2 (146) o quella di sensibilità (9). f085v resta irrisolto nel progetto RC1.4.2.
