# 001 — Test cieco della chiave lessicale di apertura del paragrafo

Stato: protocollo ESPLORATIVO; archiviare prima di leggere i risultati. Data 2026-11-13. Nessuna traduzione proposta.

## Ipotesi
H1: il primo locus P di un paragrafo funge da indice lessicale del proprio corpo, oltre il semplice vocabolario del folio. Per i token nei loci P dalla terza riga in poi, la quota che condivide i primi tre caratteri EVA con un token della prima riga del medesimo paragrafo è superiore a quella prodotta abbinando la prima riga a un diverso corpo ammissibile dello stesso folio. Un effetto robusto favorisce organizzazione per paragrafi, non identifica significati.

## Fonti fissate
- ZL3b-n.txt: SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc
- Parser RC1.2: SHA-256 8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5
- Secondo controllo IT2a-n.txt: SHA-256 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5; non usare per confermare finché il parser non è riconciliato.

## Popolazione e regole
Parser RC1.2, soli loci P non vuoti, in ordine fisico. Un paragrafo comincia al primo locus del folio o quando la riga sorgente contiene `<%>`, e termina davanti al prossimo marcatore o folio. Includere paragrafi con >=3 loci e almeno due token alfabetici EVA di lunghezza >=3 nella prima riga. Corpo: tutti i token alfabetici di lunghezza >=3 dalla terza riga in avanti. Richiedere >=1 token nel corpo. Folii eleggibili: almeno 2 paragrafi eleggibili. Non includere rosette prive di coppie. Nessun filtro in base ai valori osservati.

## Test e statistiche
Statistica primaria: quota di token nel corpo con prefisso EVA di 3 caratteri presente nella prima riga associata; pesatura per token nel corpo. Confronto con 1.999 permutazioni casuali delle prime righe tra i paragrafi eleggibili di ciascun folio, preservando ogni corpus di corpo, lunghezze e struttura; permutazioni con punti fissi consentiti. Seed NumPy PCG64 = 20261113. Test monodirezionale positivo, p = (1 + numero di null >= osservato) / 2000. O/E e differenza rispetto alla media null. Criterio H1 sostenuta esplorativamente solo se p<=0.01 sia nei due split indipendenti per folio e se le due differenze sono positive. In caso contrario, smentita rispetto a questa statistica; se pochi folii (<20 in uno split), inconcludente.

Split senza apprendimento: byte zero di SHA-256 del folio codificato ASCII, pari vs dispari, indipendente dalle righe. I due split non possono condividere folii; non si ottimizza la scelta delle features.

Secondaria: coincidenza di parole intere, stessi criteri ma non usata per il verdetto. Intervalli 95% delle differenze osservato - valore atteso per folio tramite 1.999 bootstrap stratificati sui folii dello split (seed = 20261114), con atteso calcolato come media aritmetica di tutte le associazioni prima-riga/corpo nel folio.

Generatore rivale di controllo: scambia i token fra tutte le righe P all'interno di ciascun folio preservando esattamente token totali e lunghezza in token delle righe e gli stessi confini dei paragrafi. Esegui 199 simulazioni (seed = 20261115) e riporta il valore medio del primario, senza usarlo per la decisione. Questo rivale distrugge clustering lessicale locale ma preserva la distribuzione del vocabolario in folio; non rappresenta un modello filologico completo.

## Esclusioni/interpretazione
Non sono ammessi ricalibrazioni, nuove soglie, ulteriore selezione di prefissi o decisioni sulla base dei risultati. I marker editoriali dipendono dalla traslitterazione: conclusioni semantiche o una chiave di traduzione NON sono autorizzate. Un risultato positivo è ESPLORATIVO, non VALIDATO. Test storico EXP_SEQ_LINE_MEMORY_01 studia coppie di righe, non la capacità predittiva header-corpo a distanza.
