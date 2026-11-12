from pathlib import Path
import re, csv, hashlib
base=Path('/mnt/data')
src=base/'ZL3b-n(8).txt'
expected='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
lines=src.read_text(encoding='utf-8').splitlines()
start=next(i for i,l in enumerate(lines) if l.startswith('<f70v2>'))
end=next(i for i in range(start+1,len(lines)) if re.match(r'^<f\d+[rv]\d*>\s',lines[i]))
pattern=re.compile(r'^<(f70v2\.\d+),([@&]Lz)>')
ids=[m.group(1) for l in lines[start:end] if (m:=pattern.match(l))]
assert len(ids)==len(set(ids))
assert ids==[f'f70v2.{i}' for i in list(range(2,21))+list(range(22,32))+[33]]
header=['folio','id_etichetta','id_figura','x_fig','y_fig','x_etic','y_etic','certezza','note']
model=base/'ANCHOR02_modello_etichette_f70v2.csv'
extra=base/'figure_senza_etichetta.csv'
with model.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(header)
 for id_ in ids:w.writerow(['f70v2',id_]+['']*7)
with extra.open('w',newline='',encoding='utf-8') as f:
 csv.writer(f,lineterminator='\n').writerow(header)
for p in (model,extra):
 print(p.name,'rows',sum(1 for _ in p.open())-1,'sha256',hashlib.sha256(p.read_bytes()).hexdigest())
print('input_sha256',expected)