# ANCHOR-01 — Addendum diagnostico del pilota geometrico

**Stato:** `PREPARATION_DATASET_PENDING_VALIDATION`. Questo documento non modifica la regola congelata (`SHA-256 01b4313906fb5294a294d6949d7d52d5a6c1d522d8e237352257d06ce133cce4`) né le coordinate (`SHA-256 458f5efed9591393c0b206a516a17a80282c4b6aba4ee850a87d3a08dd93e8ae`). Le soglie alternative sono **controfattuali descrittivi**, non criteri adottati e non nuovi collegamenti validati.

## Diagnostica dei 30 loci

- Distanza normalizzata del primo candidato: minimo **0.000**, mediana **0.077**, massimo **0.491**.
- Secondo candidato: minimo **0.148**, mediana **0.905**, massimo **1.798**.
- **10** distanze prime esattamente nulle. Indicano poligoni sovrapposti/tangenti o insufficiente risoluzione dei contorni, **non** un abbinamento perfetto. Il rapporto seconda/prima è indefinito.
- **3** non reciprocità del primo vicino: f70v1.15, f71r.2, f71r.10.
- **5** avvertimenti della fonte: f70v1.13, f70v1.14, f70v1.15, f70v1.16, f70v1.17.

| Raggio ipotetico | Senza candidato | Un candidato | Più candidati | Unico stabile sotto errore *assunto* | Unico stabile senza 0 px / warning / non reciprocità |
|---:|---:|---:|---:|---:|---:|
| 2 | 0 | 0 | 30 | 0 | 0 |
| 0.5 | 0 | 22 | 8 | 16 | 10 |
| 0.3 | 4 | 20 | 6 | 9 | 2 |
| 0.2 | 7 | 20 | 3 | 0 | 0 |

Le colonne "stabile" derivano **solo** dagli intervalli di sensibilità già presenti nel pacchetto, basati su una tolleranza ipotizzata, non misurata indipendentemente. **Non sono collegamenti certi, probabili o validati.** In particolare il controllo su 0 px è obbligatorio anche dove la stabilità numerica sembra buona.

## Interpretazione e vincoli

1. L'universalità di `ambiguous` a raggio 2,0 è in larga parte conseguenza della soglia permissiva e della regola che considera ambigua qualunque molteplicità. La distribuzione delle prime/seconde distanze documenta questa causa **senza cambiare il criterio**.
2. Non si può ancora attribuire tutto alla soglia: 10 sovrapposizioni di poligoni, 3 non reciprocità e 5 avvertimenti di fonte richiedono controllo delle coordinate e degli identificativi. L'esito della regola congelata resta **30/30 `ambiguous`**.
3. La metrica angolare/radiale è una possibile ipotesi per una **futura** versione, non un sostituto retroattivo. Un coefficiente 0,7 scelto ora sarebbe arbitrario; prima occorre verificare centro, anelli, orientamento e precisione dei poligoni con revisori indipendenti.
4. Non si esegue un secondo audit "indipendente" con lo stesso operatore o lo stesso modello. `review_priority.csv` è una lista di lavoro per **due revisori umani distinti**, non una scheda completata.
5. Non si esegue annotazione cieca degli attributi né analisi di potenza o inferenza su H-A3R. I 4 folii fisici restano il vincolo di dipendenza del disegno.

**Decisione:** revisione indipendente delle geometrie e delle identità dei loci prima di qualsiasi `GEOMETRY_RULE_FROZEN v2`. H-A3R **non eseguibile**; RC1.4.2, f085v e RP-01 invariati.

## Riproducibilità

Lanciare `python reproduce_diagnostic.py /percorso/ANCHOR_01_GEOMETRY_PILOT.zip /cartella/output`. Lo script verifica gli hash della regola e delle coordinate contro il lock, controlla il numero di distanze, lo stato delle schede di revisione e non riscrive il pacchetto originale. Il report è un addendum descrittivo, non una nuova preregistrazione.