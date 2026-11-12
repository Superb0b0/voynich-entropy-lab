#!/usr/bin/env python3
"""ANCHOR-02 v1.1; solo esecuzione esplicita con --corpus --labels --inventory."""
import argparse,csv,hashlib,random,re,statistics
from collections import defaultdict
from pathlib import Path

CORPUS_SHA='bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
SEED=20261113
N_PERM=20000
COMPOSITES=('cth','ckh','cph','cfh','ch','sh')
HEADER=['folio','id_etichetta','id_figura','x_fig','y_fig','x_etic','y_etic','certezza','note']

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows(path):
    with open(path,newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames:raise ValueError('CSV senza intestazione')
        return reader.fieldnames,list(reader)
def first_glyph(raw):
    # Conservativo: alternative ovunque nel locus e incognite escludono il locus.
    if '?' in raw or re.search(r'\[[^\]]*:[^\]]*\]',raw):return None
    raw=re.sub(r'<!.*?!>','',raw)
    raw=re.sub(r'<[^>]*>','',raw)
    raw=re.sub(r'\{[^}]*\}','',raw)
    raw=re.sub(r'@\d+;','',raw)
    raw=raw.lstrip('.,- =\t')
    word=re.split(r'[.,\s<]',raw,1)[0]
    if not word or not re.fullmatch(r'[a-z]+',word):return None
    for g in COMPOSITES:
        if word.startswith(g):return g
    return word[0]

def corpus_labels(path):
    if digest(path)!=CORPUS_SHA:raise ValueError('SHA-256 corpus non conforme')
    result={}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        m=re.match(r'^<(f70v2\.\d+),([^>]*)>\s+(.*)$',line)
        if m and re.search(r'[@&]L',m.group(2)):
            if m.group(1) in result:raise ValueError('locus duplicato')
            result[m.group(1)]=first_glyph(m.group(3))
    if not result:raise ValueError('nessun locus etichetta f70v2')
    return result

def load(corpus,labels,inventory):
    glyphs=corpus_labels(corpus)
    heads,inv=rows(inventory)
    if not {'id_figura','anello','pos_anello'}.issubset(heads):raise ValueError('colonne inventario mancanti')
    rings=defaultdict(list); ids=set()
    for r in inv:
        fid=r['id_figura'].strip();ring=r['anello'].strip();pos=r['pos_anello'].strip()
        if not fid or fid in ids or ring not in ('A','B') or not pos.isdigit() or int(pos)<1:raise ValueError('inventario non valido')
        ids.add(fid);rings[ring].append((int(pos),fid))
    if not rings:raise ValueError('inventario vuoto')
    for ring,rr in rings.items():
        rr.sort()
        if [x for x,_ in rr]!=list(range(1,len(rr)+1)):raise ValueError('posizioni non consecutive o duplicate')
        if len(rr)<3:raise ValueError('anello con meno di tre figure')
    fields,lab=rows(labels)
    if fields!=HEADER:raise ValueError('intestazione etichette diversa dal modello')
    if len(lab)!=len(glyphs) or {r['id_etichetta'] for r in lab}!=set(glyphs):raise ValueError('loci non coincidenti con corpus')
    byfig={};seen=set()
    for r in lab:
        loc=r['id_etichetta'];fid=r['id_figura'].strip();certainty=r['certezza'].strip()
        if loc in seen:raise ValueError('etichetta duplicata')
        seen.add(loc)
        if r['folio']!='f70v2':raise ValueError('folio non valido')
        if loc=='f70v2.33':
            if fid or certainty or any(r[k].strip() for k in ('x_fig','y_fig','x_etic','y_etic')) or r['note'].strip()!='stella centrale':raise ValueError('stella centrale non conforme')
            continue
        if certainty not in ('','alta','media','bassa'):raise ValueError('certezza non valida')
        if fid:
            if fid not in ids or fid in byfig:raise ValueError('figura assente o associazione duplicata')
            if certainty not in ('alta','media','bassa'):raise ValueError('certezza mancante')
            if not re.search(r'\btesto_visibile=(si|no)\b',r['note']):raise ValueError('visibilita testo non dichiarata')
            for k in ('x_fig','y_fig','x_etic','y_etic'):
                if r[k].strip() and not 0<=float(r[k])<=1000:raise ValueError('coordinate fuori range')
            byfig[fid]=(certainty,glyphs[loc])
        elif certainty:raise ValueError('certezza senza figura')
    return rings,byfig

def calc(rings,byfig,allowed,seed):
    fixed={f:g for f,(c,g) in byfig.items() if c in allowed and g is not None}
    edges=[];positions=defaultdict(list)
    for ring,rr in rings.items():
        ff=[fid for _,fid in rr]
        positions[ring]=[f for f in ff if f in fixed]
        edges.extend((a,b) for a,b in zip(ff,ff[1:]+ff[:1]) if a in fixed and b in fixed)
    obs=sum(fixed[a]==fixed[b] for a,b in edges)
    rng=random.Random(seed); perms=[]
    for _ in range(N_PERM):
        shuffled={}
        for ring in sorted(positions):
            fs=positions[ring];gs=[fixed[f] for f in fs];rng.shuffle(gs)
            shuffled.update(zip(fs,gs))
        perms.append(sum(shuffled[a]==shuffled[b] for a,b in edges))
    mu=statistics.mean(perms)
    p=(1+sum(abs(v-mu)>=abs(obs-mu)-1e-12 for v in perms))/(N_PERM+1)
    ordered=sorted(perms)
    return len(fixed),len(edges),obs,mu,ordered[499],ordered[19499],p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',required=True);ap.add_argument('--labels',required=True);ap.add_argument('--inventory',required=True)
    args=ap.parse_args()
    rings,byfig=load(args.corpus,args.labels,args.inventory)
    primary=calc(rings,byfig,{'alta'},SEED)
    print('analisi,unita,coppie,S,media_perm,perc2_5,perc97_5,p,verdetto')
    if primary[0]<20 or primary[1]<15:
        print(f'primaria,{primary[0]},{primary[1]},,,,,,INCONCLUSIVO')
    else:
        print('primaria,'+','.join(map(str,primary))+','+('POSITIVO' if primary[-1]<.05 else 'NULLO'))
    sens=calc(rings,byfig,{'alta','media'},SEED)
    print('sensibilita,'+','.join(map(str,sens))+',DESCRITTIVA')
    for name,p in [('corpus',args.corpus),('etichette',args.labels),('inventario',args.inventory),('script',__file__)]:print('SHA256',name,digest(p))

if __name__=='__main__':main()