#!/usr/bin/env python3
"""002: preregistered Currier A/B interaction in paragraph header key effect."""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import numpy as np

SEED_PERM = 20261116
SEED_BOOT = 20261117
N_PERM = 1999
N_BOOT = 1999
ONE_SHA = '9abeb6c9ab9dde1c055f3432c0c4c93016f14e06edd8eabd8a3605027e8bc405'


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--parser',type=Path,required=True)
    p.add_argument('--one',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    assert hashlib.sha256(a.one.read_bytes()).hexdigest()==ONE_SHA
    spec=importlib.util.spec_from_file_location('attempt001',a.one)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    folios,audit=m.load(a.corpus,a.parser)
    hdr={}
    for ln in a.corpus.read_text(encoding='utf-8').splitlines():
        mm=re.match(r'^<(f[0-9]+[rv][0-9]*|fRos)>\s*<!.*?\$L=([AB])(?=\s|>|$)',ln)
        if mm: hdr[mm.group(1)]=mm.group(2)
    values={}
    for f,dat in folios.items():
        mm3,mmw,n=m.matrices(dat)
        values[f]={'split':dat['split'], 'label':hdr.get(f,'?'), 'tokens':n,
                   'paragraphs':len(mm3), 'folio_P_rows':len(dat['rows']),
                   'delta_prefix3':float(np.trace(mm3)-mm3.sum()/len(mm3)),
                   'delta_exact':float(np.trace(mmw)-mmw.sum()/len(mmw))}
    selected={f:v for f,v in values.items() if v['label'] in ['A','B']}
    out={'config':{'seed_permutation':SEED_PERM,'seed_bootstrap':SEED_BOOT,
                   'permutations':N_PERM,'bootstraps':N_BOOT},
         'input_sha256':{'ZL3b':m.SHA_CORPUS,'parser':m.SHA_PARSER,'attempt001':ONE_SHA},
         'status':'ESPLORATIVO','eligible_folios_total':len(values),
         'eligible_folios_currier_ab':len(selected),
         'excluded_unknown_folios':sorted(f for f,v in values.items() if v['label']=='?'),
         'splits':{}}
    rng=np.random.default_rng(SEED_PERM)
    b_rng=np.random.default_rng(SEED_BOOT)
    for s in [0,1]:
        ff=sorted(f for f,v in selected.items() if v['split']==s)
        dd=np.array([selected[f]['delta_prefix3'] for f in ff])
        ddex=np.array([selected[f]['delta_exact'] for f in ff])
        tok=np.array([selected[f]['tokens'] for f in ff])
        labs=np.array([selected[f]['label'] for f in ff])
        mask=labs=='A'
        a_n=int(mask.sum());b_n=int((~mask).sum())
        def effect(mask, values=dd):
            return float(values[mask].sum()/tok[mask].sum()-values[~mask].sum()/tok[~mask].sum())
        obs=effect(mask)
        perm=np.empty(N_PERM)
        for k in range(N_PERM):
            shuffled=rng.permutation(mask)
            perm[k]=effect(shuffled)
        boots=np.empty(N_BOOT)
        ia=np.flatnonzero(mask);ib=np.flatnonzero(~mask)
        for k in range(N_BOOT):
            sa=b_rng.choice(ia,size=a_n,replace=True)
            sb=b_rng.choice(ib,size=b_n,replace=True)
            boots[k]=dd[sa].sum()/tok[sa].sum()-dd[sb].sum()/tok[sb].sum()
        out['splits'][str(s)]={'A_folios':a_n,'B_folios':b_n,
            'A_delta_per_token':float(dd[mask].sum()/tok[mask].sum()),
            'B_delta_per_token':float(dd[~mask].sum()/tok[~mask].sum()),
            'contrast_A_minus_B':obs,'null_mean':float(perm.mean()),
            'p_two_sided':float((1+np.count_nonzero(np.abs(perm)>=abs(obs)))/(N_PERM+1)),
            'null_q025_q975':[float(x) for x in np.quantile(perm,[.025,.975])],
            'bootstrap_CI95':[float(x) for x in np.quantile(boots,[.025,.975])],
            'secondary_exact_word_contrast':effect(mask,ddex)}
    ss=list(out['splits'].values())
    if min(min(x['A_folios'],x['B_folios']) for x in ss)<20:
        out['verdict']='INCONCLUDENTE - insufficient group folios'
    elif (ss[0]['contrast_A_minus_B']*ss[1]['contrast_A_minus_B']>0 and
          all(x['p_two_sided']<=.01 for x in ss) and
          all(x['bootstrap_CI95'][0]*x['bootstrap_CI95'][1]>0 for x in ss)):
        out['verdict']='H2 SOSTENUTA SOLO ESPLORATIVAMENTE'
    else:
        out['verdict']='H2 NON SOSTENUTA'
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False))

if __name__=='__main__':main()
