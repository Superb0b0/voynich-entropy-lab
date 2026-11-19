# Attempt 008 - VOY-DEPEND-01: la ripetizione della classe iniziale modifica il riuso lessicale del corpo riga?
Data: 2026-11-14. Stato: ESPLORATIVO. Sostituisce VOY-XJOINT-01 (test di sola coesistenza, non discriminante per una causa comune).

## Domanda
Dentro il paragrafo, nelle coppie di righe consecutive, quando la classe della prima parola si ripete il riuso lessicale del corpo della riga successiva e' diverso rispetto alle coppie in cui non si ripete, a parita' di lunghezza delle due righe e a parita' di posizione (esclusi gli estremi del paragrafo)?

## Dati e confini
- Solo ZL3b-n.txt training-only da $VOYNICH_DATA_DIR (SHA-256 atteso dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9; lo script si ferma se diverso). Holdout non aperto.
- Contaminazione storica, da mantenere nella classificazione: l'effetto di riuso fra righe (LINE_MEMORY) e' stato misurato in passato sul corpus completo, quindi su questi dati NON e' una scoperta indipendente; qo->qo (004, QO-RIVAL-03) e' stato misurato sul training. Questo attempt controlla la dipendenza fra i due, non conferma nessuno dei due effetti.
- Parser primario: estrazione semplificata come in 003/004/005 (righe P, rimozione di <...>, {...}, [...]; separatori punto, virgola, spazio; minuscole a-z). Variante B (sola sensibilita'): [a:b] sostituito dalla prima variante a invece di essere rimosso.
- Unita': paragrafo (*P/@P apre un paragrafo); righe numerate consecutive; split per folio con SHA256(foglio+':20261114') pari/dispari (come 003/004/005).

## Definizioni
- Testa = prima parola della riga; corpo = tutte le parole successive. Classe della testa per prefisso: qo, ch, sh, d, o, y, s, altro.
- Coppia (i, i+1) di righe consecutive nello stesso paragrafo, con corpo non vuoto in entrambe. X = 1 se le due teste hanno la stessa classe (qualsiasi, 'altro' incluso), altrimenti 0.
- Y = frazione dei token del corpo della riga i+1 presenti nel corpo della riga i (testa esclusa da entrambe: il risultato non dipende meccanicamente dalle teste).
- Strati: 9 celle = fascia di lunghezza del corpo i+1 (1-3, 4-6, 7+) x fascia di lunghezza del corpo i (1-3, 4-6, 7+).
- Statistica primaria S_adj = somma sulle celle con almeno una coppia X=1 e una X=0 di w_c * (media Y|X=1 - media Y|X=0), con w_c proporzionale al numero di coppie X=1 della cella.
- Analisi PRIMARIA: solo coppie interne (esclusa ogni coppia che contiene la prima o l'ultima riga del paragrafo). Nullo: permutazione uniforme delle teste fra le righe interne del paragrafo, corpi fermi, estremi fissi. Il nullo conserva composizione delle classi, lunghezze e corpi.

## Criterio (fissato prima di eseguire)
1. Calibrazione obbligatoria (sul training, stessa struttura): (a) dimensione: su 60 dataset con teste permutate la frazione di rifiuti a p<=0,025 deve essere <= 0,07; (b) potenza: su 60 dataset con dipendenza piantata (nelle coppie con X=1, con probabilita' 0,25 un token del corpo i+1 sostituito con uno del corpo i) la frazione di rifiuti deve essere >= 0,60. Altrimenti verdetto NON INTERPRETABILE.
2. Numerosita': almeno 30 coppie interne con X=1 in ciascuno split, altrimenti NON VALUTABILE.
3. SUPPORTED se in ENTRAMBI gli split: p a due code <= 0,025, stesso segno di S_adj, |S_adj| >= 0,15 x (media di Y fra le coppie X=0 dello split). Altrimenti NOT SUPPORTED.
- Permutazioni principali: 1999. Calibrazione: 199 permutazioni per dataset. Seme 20261122.

## Descrittivi e sensibilita' (nessun peso sul verdetto)
Versione con tutte le coppie (estremi inclusi, nullo che permuta tutte le teste); parser variante B; S non stratificata; leave-one-folio-out (frazione di esclusioni con lo stesso segno); conteggio delle coppie qo->qo interne (nessuna inferenza: numerosita' troppo piccola).

## Limiti
Classi per prefisso arbitrarie; scambiabilita' delle teste dentro il paragrafo ignora colonna, mano, A/B; Y non distingue riuso lessicale da somiglianza grafica; un'associazione non dimostra una causa comune (potrebbe dipendere da frequenza delle parole o da altre caratteristiche del folio, controllate solo per lunghezza); l'ipotesi nasce da dati gia' studiati. Non qualificante secondo PROTOCOL.md v1 (nessun rivale Timm-Schinner). CI non ancora eseguita.
