#!/usr/bin/env python3
"""Exploratory Voynich analysis fixed 2026-11-11. RC1.2 P lines, no 6-10 token filter.
A/B, L>=4, outcome first word starts 'qo', folio cluster bootstrap 2000 seed 20261111.
This program does not alter EXP-SEQ-03 frozen files.
"""
from pathlib import Path
import re,json,hashlib,sys
import numpy as np
import pandas as pd
from collections import defaultdict,Counter
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from scipy.special import expit
import statsmodels.api as sm
ROOT=Path('/mnt/data/EXP_SEQ_05_EXPLORATORY');N_BOOT=2000;SEED=20261111
PAGE=re.compile(r'^<([^>]+)>\s*(.*)$');TAGS={'*P0','*Pb','+P0','+P1','+Pb','+Pc','+Pr','=P0','=Pt','@P0','@P1','@Pb'}
KW={'<$>','<%>','<->','<~>','<d>','<@H=2>','<@H=3>'}
def clean(s):
    s=re.sub(r'<![^>]*>',' ',s)
    for marker in KW:s=s.replace(marker,' ')
    s=re.sub(r'\[[^\[\]]*\]',' ',s).replace('{','').replace('}','')
    return re.findall(r'[A-Za-z]+',s.lower())
def folio_of(p):
    return p.split('.')[0]
def locus_number(p):
    return int(p.rsplit('.',1)[1])
def canon_group(p):
    m=re.match(r'^f(\d+)([rv])\d*$',p)
    return 'f'+m.group(1)+m.group(2) if m else p

def read(path):
    data=path.read_bytes();digest=hashlib.sha256(data).hexdigest(); metadata={};lines=[];last=None
    for n,s in enumerate(data.decode('utf-8').splitlines(),1):
        m=PAGE.match(s)
        if not m:continue
        key,body=m.groups()
        if ',' not in key:
            if re.fullmatch(r'f(?:\d+[rv]\d*|Ros)',key):
                metadata[key]=dict(re.findall(r'\$([A-Z])=([^\s>]+)',body))
            continue
        loc,tag=key.split(',',1)
        if tag not in TAGS:continue
        page=folio_of(loc);mt=metadata.get(page,{})
        ts=clean(body)
        if not ts:continue
        row=dict(loc=loc,page=page,folio=canon_group(page),j_page=locus_number(loc),lang=mt.get('L'),hand=mt.get('H'),quire=mt.get('Q'),illus=mt.get('I'),n=len(ts),chars=sum(map(len,ts)),starts='<%>' in body,ends='<$>' in body,first=int(ts[0].startswith('qo')),firstword=ts[0],r_n=max(0,len(ts)-1),r_qo=sum(t.startswith('qo') for t in ts[1:]))
        row['class']=next((name for name,flag in [('qo',ts[0].startswith('qo')),('d',ts[0].startswith('d')),('ch',ts[0].startswith('ch')),('sh',ts[0].startswith('sh')),('o',ts[0].startswith('o')),('y',ts[0].startswith('y')),('gallows',ts[0][0] in 'ktpf' or ts[0].startswith(('cth','ckh','cph','cfh')))] if flag),'other')
        lines.append(row)
    issues=[];by_page=defaultdict(list)
    for r in lines:by_page[r['page']].append(r['j_page'])
    for page,nums in by_page.items():
        if any(y<=x for x,y in zip(nums,nums[1:])):issues.append(page)
    blocks=[];cur=[];lastpage=None
    def close():
        nonlocal cur
        if cur and len(cur)>=4 and len({r['lang'] for r in cur})==1 and cur[0]['lang'] in ('A','B'):
            blocks.append(cur)
        cur=[]
    for r in lines:
        if r['page']!=lastpage:close();lastpage=r['page']
        if r['starts']:close()
        if cur or r['starts']:cur.append(r)
        if r['ends']:close()
    close()
    out=[]
    for b in blocks:
        L=len(b);start=b[0]['loc']
        for j,r in enumerate(b,1):
            x={k:v for k,v in r.items() if k not in ('firstword','starts','ends')}
            x.update(j_par=j,L=L,rel=(j-1)/(L-1),rel_bin=min(4,int(5*(j-1)/(L-1))),block=start,band=int(j in (3,4)),old=int(j in(1,2)))
            out.append(x)
    return pd.DataFrame(out), dict(hash=digest,all_P_loci=len(lines),paragraphs=len(blocks),nonmonotone_pages=issues,metadata_pages=len(metadata),all_P_token_count=sum(r['n'] for r in lines))

def ci_from_vectors(d, vectors, fn):
    """Two thousand resamples of whole folios, computed from their sufficient statistics."""
    folios=sorted(d.folio.unique());F=len(folios)
    if F<2:return [None,None]
    agg=np.asarray([np.asarray(vectors(d[d.folio==f]),dtype=float) for f in folios]);
    rng=np.random.default_rng(SEED)
    picks=rng.integers(0,F,size=(N_BOOT,F));
    vals=agg[picks].sum(axis=1); v=np.array([fn(row) for row in vals]);v=v[np.isfinite(v)]
    return np.quantile(v,[.025,.975]).tolist() if len(v) else [None,None]

def ci_mean(d,col):
    return ci_from_vectors(d,lambda z:[z[col].sum(),len(z)],lambda v:v[0]/v[1] if v[1] else np.nan)

def ci_band(d,col='first'):
    return ci_from_vectors(d,lambda z:[z.loc[z.j_par.isin([3,4]),col].sum(),z.j_par.isin([3,4]).sum(),z.loc[z.j_par.isin([1,2]),col].sum(),z.j_par.isin([1,2]).sum()],lambda v:v[0]/v[1]-v[2]/v[3] if min(v[1],v[3]) else np.nan)

def ci_specific(d):
    def vf(z):
        z0=z[z.j_par.isin([1,2])];z1=z[z.j_par.isin([3,4])]
        def st(v):
            r=(v.r_qo/v.r_n.replace(0,np.nan)).dropna()
            return [v['first'].sum(),len(v),r.sum(),len(r)]
        return st(z1)+st(z0)
    return ci_from_vectors(d,vf,lambda v:(v[0]/v[1]-v[4]/v[5])-(v[2]/v[3]-v[6]/v[7]) if all(v[i]>0 for i in (1,3,5,7)) else np.nan)

def get_profile(df):
    out=[]
    for j in range(1,9):
        t=df[df.j_par==j];s=int(t['first'].sum());n=len(t)
        out.append(dict(j=j,n=n,yes=s,rate=s/n if n else None,folios=t.folio.nunique(),ci=ci_mean(t,"first") if n else [None,None]))
    return out

def logistic_effect(d,controls):
    dd=d[d.j_par<=4].copy();y=dd['first'].to_numpy().astype(float)
    if len(np.unique(y))<2:return dict(status='NOT_ESTIMABLE')
    numeric=['band']+(['chars','L'] if controls else [])
    cats=(['hand','quire','illus','lang'] if controls else [])
    x=pd.DataFrame({'const':1.,'band':dd.band.astype(float)})
    if controls:
        for col in ['chars','L']:x[col]=dd[col].astype(float)
        for col in cats:
            if dd[col].nunique(dropna=False)>1:
                mat=pd.get_dummies(dd[col].fillna('MISSING').astype(str),prefix=col,drop_first=True,dtype=float)
                x=pd.concat([x,mat],axis=1)
    X=x.to_numpy(dtype=float);G=dd.folio.to_numpy();
    try:
        model=sm.GLM(y,X,family=sm.families.Binomial()).fit(maxiter=100,disp=0)
        try:rob=model.get_robustcov_results(cov_type='cluster',groups=G)
        except AttributeError:rob=sm.GLM(y,X,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':G},maxiter=100,disp=0)
        bi=list(x.columns).index('band');p0=expit(X@np.asarray(model.params)-np.asarray(model.params)[bi]*X[:,bi]);p1=expit(X@np.asarray(model.params)+np.asarray(model.params)[bi]*(1-X[:,bi]));
        return dict(coef=float(model.params[bi]),se_cluster=float(rob.bse[bi]),marginal_effect=float(np.mean(p1-p0)),n=len(dd),variables=x.columns.tolist(),model_converged=bool(model.converged))
    except Exception as ex:return dict(status='NOT_ESTIMABLE',reason=repr(ex)[:300],variables=x.columns.tolist())

def e1(df):
    out={}
    for group in ['A','B','ALL']:
        d=df if group=='ALL' else df[df.lang==group];s=d[d.j_par<=4];before=s[s.j_par.isin([1,2])];after=s[s.j_par.isin([3,4])];
        contrast=lambda t:float(t[t.j_par.isin([3,4])]['first'].mean()-t[t.j_par.isin([1,2])]['first'].mean())
        ci=ci_band(s);rate0=float(before['first'].mean());rate1=float(after['first'].mean());simple=logistic_effect(d,False);adjusted=logistic_effect(d,True)
        decrease=1-abs(adjusted.get('coef',np.nan))/max(abs(simple.get('coef',np.nan)),1e-10)
        out[group]=dict(n_paragraphs=d.block.nunique(),n_folios=d.folio.nunique(),profile=get_profile(d),early=dict(y=int(before['first'].sum()),n=len(before),rate=rate0),late=dict(y=int(after['first'].sum()),n=len(after),rate=rate1),delta=rate1-rate0,delta_ci=ci,logit_unadjusted=simple,logit_adjusted=adjusted,coef_reduction_fraction=float(decrease),covariates_explain_gt_half=bool(decrease>.5),robust=bool(rate1-rate0>=.10 and ci[0]>0))
    return out

def make_pipe(poscol,d):
    c=['lang','hand','quire','illus',poscol] if poscol in ['j_par','j_page','rel_bin'] else []
    nc=['chars','L'];dd=d.copy()
    for col in c:dd[col]=dd[col].fillna('MISSING').astype(str)
    ct=ColumnTransformer([('categorical',OneHotEncoder(handle_unknown='ignore'),c),('numeric',StandardScaler(),nc)])
    return Pipeline([('ct',ct),('lr',LogisticRegression(C=1,solver='lbfgs',max_iter=300,random_state=SEED))]),dd[c+nc]

def e2(df):
    d=df[df.j_par<=8].copy();d['rel_bin']=d['rel_bin'].astype(str)
    X=d;y=d['first'].to_numpy();fol=d['folio'].to_numpy()
    if len(np.unique(fol))<5:return dict(status='NOT_ESTIMABLE',reason='Few folios')
    folds=list(GroupKFold(n_splits=5).split(d,y,fol));losses={};meta=[]
    for pos in ['j_par','j_page','rel_bin']:
        p=np.full(len(d),np.nan)
        for i,(tr,te) in enumerate(folds):
            model,features=make_pipe(pos,d);model.fit(features.iloc[tr],y[tr]);p[te]=model.predict_proba(features.iloc[te])[:,1]
        p=np.clip(p,1e-12,1-1e-12)
        losses[pos]=-(y*np.log(p)+(1-y)*np.log1p(-p))
    contrasts={}
    for first,second in [('j_par','j_page'),('j_par','rel_bin'),('j_page','rel_bin')]:
        diff=losses[second]-losses[first]
        tmp=d[['folio']].copy();tmp['delta']=diff
        ci=ci_mean(tmp,'delta');mu=float(diff.mean())
        contrasts[f'{first}_vs_{second}']=dict(mean=mu,ci=ci,preferred=first if mu>=.01 and ci[0]>0 else (second if mu<=-.01 and ci[1]<0 else 'INCONCLUSIVE'))
    return dict(n_rows=len(d),n_folios=d.folio.nunique(),n_paragraphs=d.block.nunique(),mean_logloss={key:float(v.mean()) for key,v in losses.items()},contrasts=contrasts,folds=[dict(test_n=len(te),test_folios=len(np.unique(fol[te]))) for tr,te in folds],jpage_status='MONOTONE_IN_SOURCE' )

def class_probs(s):
    return s['class'].value_counts().reindex(['qo','d','ch','sh','o','y','gallows','other'],fill_value=0)

def e3(df):
    result={}
    for group in ['A','B','ALL']:
        d=df if group=='ALL' else df[df.lang==group];t=d[d.j_par<=4].copy();early=t[t.j_par.isin([1,2])];late=t[t.j_par.isin([3,4])]
        def calc(z):
            z0=z[z.j_par.isin([1,2])];z1=z[z.j_par.isin([3,4])];
            f0=z0['first'].mean();f1=z1['first'].mean();
            # Mean rest fraction per line (not token-weighted) where rest exists
            rr0=(z0['r_qo']/z0['r_n'].replace(0,np.nan)).mean();rr1=(z1['r_qo']/z1['r_n'].replace(0,np.nan)).mean();
            return (f1-f0)-(rr1-rr0)
        spec=float(calc(t));ci=ci_specific(t);r0=float((early['r_qo']/early['r_n'].replace(0,np.nan)).mean());r1=float((late['r_qo']/late['r_n'].replace(0,np.nan)).mean());DR=r1-r0
        table={}
        for j in range(1,9):
            z=d[d.j_par==j];table[str(j)]=dict(r_n=int(z.r_n.sum()),r_qo=int(z.r_qo.sum()),token_rate=(float(z.r_qo.sum()/z.r_n.sum()) if z.r_n.sum() else None),line_rest_mean=float((z.r_qo/z.r_n.replace(0,np.nan)).mean()) if len(z) else None,lines=len(z))
        cl0=class_probs(early);cl1=class_probs(late)
        result[group]=dict(n_paragraphs=d.block.nunique(),n_folios=d.folio.nunique(),first_early=dict(y=int(early['first'].sum()),n=len(early)),first_late=dict(y=int(late['first'].sum()),n=len(late)),rest_early=dict(y=int(early.r_qo.sum()),n=int(early.r_n.sum()),mean_per_line=r0),rest_late=dict(y=int(late.r_qo.sum()),n=int(late.r_n.sum()),mean_per_line=r1),D_F=float(late['first'].mean()-early['first'].mean()),D_R=DR,D_specific=spec,D_specific_ci=ci,opening_enrichment=bool(spec>=.10 and ci[0]>.0),row_effect=bool(DR>=.05),rest_position=table,classes=dict(early=cl0.to_dict(),late=cl1.to_dict(),diff_pp=((cl1/len(late)-cl0/len(early))*100).to_dict()),class_sum_verified=(cl0.sum()==len(early) and cl1.sum()==len(late)))
    return result

def main():
    path=Path(sys.argv[1]);d,m=read(path);report=dict(method=dict(status='EXPLORATORY_NOT_PREREGISTERED',source=str(path),source_hash=m['hash'],parser='RC1.2',P='all',min_paragraph_lines=4,no_6_10_filter=True,cluster='folio',bootstrap=N_BOOT,seed=SEED,first_token='qo initial two characters',first_eight_lines_only_for_profile_CV=True,measure_line_length='sum of letters in all cleaned tokens',relative='(j_par-1)/(L-1) five fixed bins',gallows_benched_in_gallows=True),counts=m,cohort=dict(n=len(d),paragraphs=d.block.nunique(),folios=d.folio.nunique(),A_par=d[d.lang=='A'].block.nunique(),B_par=d[d.lang=='B'].block.nunique()))
    if m['nonmonotone_pages']:
        report['analysis2']=dict(status='NOT_ESTIMABLE_NONMONOTONIC_PAGE_LOCI',pages=m['nonmonotone_pages'])
    report['analysis1']=e1(d)
    if not m['nonmonotone_pages']:report['analysis2']=e2(d)
    report['analysis3']=e3(d)
    output=ROOT/(path.stem+'_results.json');output.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=True,default=lambda x:x.item() if hasattr(x,'item') else x))
    print(json.dumps(dict(output=str(output),cohort=report['cohort'],a1={k:{p:v for p,v in x.items() if p!='profile'} for k,x in report['analysis1'].items()},a2=report['analysis2'],a3={k:{p:v for p,v in x.items() if p not in ['rest_position','classes']} for k,x in report['analysis3'].items()}),ensure_ascii=False,default=str))
if __name__=='__main__':main()
