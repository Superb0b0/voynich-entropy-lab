#!/usr/bin/env python3
"""EXP-SEQ-05 four-scenario sensitivity audit (PHYSICAL folio bootstrap, exploratory).

Reuses the exact historical analysis.py read() for <%> / <$> block construction,
RC1.2 cleaning, metadata and page/folio normalization. Performs separate A/B
physical-folio cluster bootstrap with a fixed seed. Recto and verso are pooled;
fRos, which is not a numeric physical folio, is a separate exceptional cluster.

Outputs aggregated CSV + JSON only. Does not export text or folio identities.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import numpy as np

CORPUS_SHA = 'bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc'
HISTORICAL_SHA = '4b40c6827b2d8520fe4f1fbdc1a3341298bc631b4242f037d1eebfec9a4b7773'
N_BOOT = 10000
SEED = 20261110
FIELDS = ['group','line_perimeter','token_filter','blocks','raw_page_ids','folio_side_clusters','physical_folio_clusters',
          'early_qo','early_n','early_pct','late_qo','late_n','late_pct','delta_pp',
          'bootstrap_ci_low_pp','bootstrap_ci_high_pp']


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_historical(path: Path):
    spec=importlib.util.spec_from_file_location('exp_seq_05_historical_read_only',path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Historical source not importable')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bootstrap(df, seed: int, n_boot: int):
    # One row per physical folio (both r/v, including panels); all of its blocks
    # stay together. Bootstrap resamples physical folios with replacement.
    cluster=[]
    for folio, z in df.groupby('physical_folio',sort=True):
        a=z[z.j_par.isin((1,2))]
        b=z[z.j_par.isin((3,4))]
        cluster.append((int(a['first'].sum()),len(a),int(b['first'].sum()),len(b)))
    if len(cluster) < 2:
        return (None,None)
    c=np.asarray(cluster,dtype=np.float64)
    n=len(c)
    rng=np.random.default_rng(seed)
    # Memory bounded in batches to allow large F on normal hardware.
    estimates=[]
    for _ in range((n_boot+999)//1000):
        count=min(1000,n_boot-len(estimates))
        choices=rng.integers(0,n,size=(count,n))
        sums=c[choices].sum(axis=1)
        e=sums[:,0]/sums[:,1]
        l=sums[:,2]/sums[:,3]
        estimates.extend(((l-e)*100).tolist())
    lo,hi=np.quantile(estimates,[.025,.975],method='linear')
    return (round(float(lo),4),round(float(hi),4))


def run(corpus: Path, historical: Path, out: Path, n_boot: int, seed: int):
    assert sha(corpus)==CORPUS_SHA, 'FAIL CLOSED corpus SHA-256 mismatch'
    assert sha(historical)==HISTORICAL_SHA, 'FAIL CLOSED historical script SHA-256 mismatch'
    parser=load_historical(historical)
    df, metadata=parser.read(corpus)
    assert metadata['all_P_loci']==4130, metadata
    assert metadata['all_P_token_count']==35492, metadata
    assert metadata['paragraphs']==491, metadata
    # Physical folio merges r and v, unlike the historical 'folio' field which
    # contains a side suffix. Reject unexpected A/B label shapes; fRos is the only exceptional unit.
    page_ids=df['page'].unique()
    bad=[x for x in page_ids if not re.fullmatch(r'f(?:\d+[rv]\d*|Ros)',str(x))]
    if bad: raise RuntimeError(f'FAIL CLOSED: {len(bad)} unexpected folio IDs in A/B dataset')
    df=df.copy()
    df['physical_folio']=df['page'].str.extract(r'^(f\d+)[rv]\d*$')[0].fillna(df['page'])
    rows=[]
    for max_lines, line_perimeter in [(9,'4-9'),(None,'4+')]:
        for filtered in (False, True):
            for group in ('A','B'):
                subset=df[df['lang'].eq(group)]
                if max_lines is not None:
                    subset=subset[subset['L'].le(max_lines)]
                if filtered:
                    # Filter by the first FOUR line counts. Block IDs remain
                    # unique within an A/B population (folio,page,first locus).
                    first4=subset[subset['j_par'].le(4)]
                    is_ok=(first4.groupby('block')['n']
                           .agg(lambda x: len(x)==4 and x.between(6,10).all()))
                    eligible=set(is_ok[is_ok].index)
                    subset=subset[subset['block'].isin(eligible)]
                e=subset[subset.j_par.isin((1,2))]
                l=subset[subset.j_par.isin((3,4))]
                assert len(e)==len(l)==2*subset.block.nunique(), 'Unexpected block accounting'
                early=int(e['first'].sum());late=int(l['first'].sum())
                # Avoid conflating raw page IDs with normalized folio clusters.
                low,high=bootstrap(subset,seed,n_boot)
                n=len(e)
                row=dict(group=group,line_perimeter=line_perimeter,token_filter='6-10' if filtered else 'none',
                         blocks=int(subset.block.nunique()),raw_page_ids=int(subset.page.nunique()),
                         folio_side_clusters=int(subset.folio.nunique()),
                         physical_folio_clusters=int(subset.physical_folio.nunique()),
                         early_qo=early,early_n=n,early_pct=round(100*early/n,4),
                         late_qo=late,late_n=n,late_pct=round(100*late/n,4),
                         delta_pp=round(100*(late-early)/n,4),
                         bootstrap_ci_low_pp=low,bootstrap_ci_high_pp=high)
                rows.append(row)
    cluster_checks={('A','4-9','none'):50,('B','4-9','none'):38,
      ('A','4-9','6-10'):40,('B','4-9','6-10'):11,
      ('A','4+','none'):54,('B','4+','none'):41,
      ('A','4+','6-10'):49,('B','4+','6-10'):16}
    for row in rows:
      assert row['physical_folio_clusters']==cluster_checks[(row['group'],row['line_perimeter'],row['token_filter'])],row
    baseline={('A','4-9','6-10'):(75,5,47),('B','4-9','6-10'):(30,6,19)}
    for row in rows:
        key=(row['group'],row['line_perimeter'],row['token_filter'])
        if key in baseline:
            assert (row['blocks'],row['early_qo'],row['late_qo'])==baseline[key],row
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    report={'status':'EXPLORATORY_DESCRIPTIVE_SENSITIVITY',
            'corpus_sha256':sha(corpus), 'historical_script_sha256':sha(historical),
            'pipeline':'historical EXP-SEQ-05 analysis.py read() with RC1.2 equivalent tokens and <%>...<$> blocks',
            'scope':'A/B homogeneous 4+ P-line blocks on full corpus, no independent holdout',
            'bootstrap':{'unit':'physical folio f<number> merges recto and verso; fRos exceptional nonnumeric unit is kept as one separate cluster',
                         'method':'cluster-resample physical folios with replacement, retain all r/v and all blocks, weight each block equally in each sample',
                         'seed':seed,'repetitions':n_boot,'percentiles':[2.5,97.5],
                         'stratification':'separate A and B',
                         'fRos_exception':'B includes fRos as a nonnumeric exceptional cluster in unfiltered conditions; do not call it an ordinary physical folio',
                         'quantile_method':'numpy.quantile(method=linear), interpolation between ordered bootstrap estimates'},
            'all_P_loci':metadata['all_P_loci'],'all_P_tokens':metadata['all_P_token_count'],
            'paragraphs_4_plus':metadata['paragraphs'],
            'rows':rows,
            'caveat':'same already-explored manuscript; previous exposure, post-hoc token filter, no multiplicity adjustment; no independent scientific confirmation; folio cluster bootstrap does not control hand/quire dependence; PRED-LAYOUT-01 primary 4-9 unfiltered stated by reviewer, original predeclaration artifact not yet independently checked'}
    manifest=out.with_suffix('.json')
    manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return rows,manifest

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--historical',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--boot',type=int,default=N_BOOT)
    p.add_argument('--seed',type=int,default=SEED)
    a=p.parse_args()
    rows,manifest=run(a.corpus,a.historical,a.out,a.boot,a.seed)
    print('PASS: corpus hash, original source hash, RC1.2 totals and historical 75/30 comparison')
    print('GROUP | LENGTH | FILTER | BLOCKS | PHYSICAL FOLIOS | EARLY | LATE | DELTA pp | BOOT CI pp')
    for r in rows:
        print(f"{r['group']:5} | {r['line_perimeter']:6} | {r['token_filter']:6} | {r['blocks']:6} | {r['physical_folio_clusters']:17} | {r['early_qo']:2}/{r['early_n']:<3} | {r['late_qo']:2}/{r['late_n']:<3} | {r['delta_pp']:7.2f} | [{r['bootstrap_ci_low_pp']:.2f}, {r['bootstrap_ci_high_pp']:.2f}]")
    print('OUTPUT',a.out,manifest)
