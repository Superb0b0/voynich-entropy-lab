# VERIFICA MIRATA (non e' una CI completa)

Strumento nuovo e separato: tools/verify_targeted.py + .github/workflows/verify-targeted.yml. Non modifica tools/verify_attempts.py, gli attempt, i registri o i dati.

## Cosa fa
Rigioca gli attempt selezionati (di default quelli con numero >= 005) UNO PER UNO e per ciascuno restituisce PASS, FAIL o NON VERIFICABILE. Non si ferma al primo errore.
- PASS: replay entro tolleranza e nessuna violazione di isolamento.
- FAIL: violazione di isolamento, errore di esecuzione, output mancante o risultati diversi dal results.json archiviato.
- NON VERIFICABILE: contratto mancante (es. nessun attempt.yml), strumenti assenti, sandbox non avviabile, timeout, oppure self-test dell'isolamento non superato. Non e' un fallimento dell'attempt.

## Isolamento (tutti i livelli devono reggere)
1. L'attempt viene copiato fuori dal repo SENZA results.json (non puo' copiare la risposta attesa).
2. Namespace mount e rete nuovi: la radice del repo (con .git, data/, HOLDOUT.md, altri attempt) e' nascosta sotto un tmpfs vuoto; nessuna rete.
3. Privilegi eliminati dopo il mount (uid 65534, nessuna capability, no_new_privs): non puo' fare umount.
4. strace -f registra ogni chiamata su file e rete: qualunque percorso dentro la radice del repo, o connect non loopback, e' una violazione anche se l'accesso non riesce.

## Self-test obbligatorio
Prima di ogni verifica gira un self-test: una prova diretta che il repo e' nascosto e non smontabile, 13 attempt ostili che DEVONO fallire (lettura diretta, link simbolico, sottoprocesso, git show, GIT_DIR, .git/objects, HOLDOUT.md, risultati di altri attempt, umount, rete, copia dei risultati attesi, risultati sbagliati) e un controllo positivo che DEVE passare. Se anche uno solo si comporta diversamente, nessun attempt viene verificato (tutti NON VERIFICABILE).

## Limiti dichiarati
- Il percorso con sudo -n (non root) e Python 3.11 non erano collaudabili nel sandbox di sviluppo: il primo collaudo e' il job CI.
- La rilevazione e' per stringa di percorso: alias della radice del repo (mount aggiuntivi, bind) non sono coperti; l'occultamento nasconde il percorso esatto, la radice risolta e GITHUB_WORKSPACE.
- Non difende da exploit del kernel ne' da canali laterali. Gli attempt possono leggere file di sistema leggibili da tutti.
- Un PASS non dice che l'esperimento sia scientificamente corretto: dice che e' riproducibile e non ha toccato input protetti.
- compare(), hashes(), protected() e sanitize() sono riusati da verify_attempts.py: un loro difetto resta un difetto.

## Dicitura obbligatoria
Citare sempre l'esito come "VERIFICA MIRATA: PASS/FAIL/NON VERIFICABILE", mai come "CI verde".
