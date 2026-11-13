# 002 — Interazione Currier A/B nella presunta chiave lessicale dei paragrafi

2026-11-13; stato ESPLORATIVO. Protocollo fissato prima di leggere i risultati. Motivo: la divergenza fra split del test 001 invita a verificare un fattore codicologico preesistente, non a scegliere a posteriori il gruppo favorevole.

Ipotesi falsificabile H2: l'eccesso di overlap prefisso 3 EVA fra intestazione del paragrafo e suo corpo distante, corretto per lo scambio delle intestazioni entro folio (metriche esatte di 001), è diverso per le etichette Currier A e Currier B. Non si assume un verso A>B o B>A.

Input bloccati: ZL3b-n.txt SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc; ivtff_parser_rc1_2.py SHA-256 8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5; 001/run.py SHA-256 9abeb6c9ab9dde1c055f3432c0c4c93016f14e06edd8eabd8a3605027e8bc405. Metadati Currier esclusivamente dalla testata IVTFF di ciascun folio ($L=A o $L=B). Folii non A/B esclusi dal confronto, numerati e riferiti nel risultato. Non cambiare la popolazione 001, i prefissi o la soglia. Split per folio identico al 001 (primo byte SHA256 id folio, modulo 2).

Per ogni folio, delta esatto di token = somma della diagonale matrice(header proprio, corpo) - somma di tutti gli abbinamenti possibili / numero paragrafi. Per ciascun gruppo Currier, dividi la somma dei delta per il numero di token corpo idonei. Test di interazione: differenza delta_A - delta_B (non direzionale). Nulla: riassegnare le etichette A/B ai folii all'interno di ciascuno split con 1.999 permutazioni preservando il numero di A e B; non modificare né token né grandezze folio. Seed PCG64 = 20261116. Test due code con centro zero, p=(1+ # |delta_null| >= |delta_osservato|)/2000. Bootstrap del contrasto per folio entro ciascun gruppo, 1.999 ricampionamenti, seed = 20261117, CI95 percentile.

Decisione: H2 esplorativamente sostenuta solo se (i) ciascuno split ha almeno 20 folii per gruppo, (ii) il contrasto è dello stesso segno nei due split, (iii) p<=0,01 nei due split e (iv) CI95 dei contrasti esclude zero in entrambi. Altrimenti NON SOSTENUTA; mancanza di dimensione campionaria = INCONCLUDENTE. Questo è un test esplorativo consecutivo allo 001, non è validazione indipendente.

Rivale: modello a intestazioni scambiate entro folio come in 001, la cui aspettativa è sottratta esattamente; controllo descrittivo secondario sull'overlap parole intere, senza influire sul verdetto. Nessun esito semantico o decifrazione autorizzato.
