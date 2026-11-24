#!/usr/bin/env python3
"""VOY-REFLOW-PREREG-v1: adapter only, original estimator and reflow function extracted verbatim by AST."""
import ast,csv,hashlib,json,os,re,sys,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path(__file__).resolve().parent
SERIES=('ZL3b','IT2a','Timm')
N=1000; MASTER=20261124

def compile_functions(path,names,namespace):
    tree=ast.parse(path.read_text())
    for name in names:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),namespace)
    return tree

def initialize():
    global old, rf, paragraphs, raw_rows
    os.chdir(ROOT/'predictor')
    path=ROOT/'predictor/run.py'; tree=ast.parse(path.read_text()); old={}
    # Original imports, constants, estimator, feature function and bootstrap are unmodified.
    for n in tree.body:
        if isinstance(n,(ast.Import,ast.ImportFrom)) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SEED','INPUTS','OPENERS') for t in n.targets)):
            exec(compile(ast.Module(body=[n],type_ignores=[]),str(path),'exec'),old)
    compile_functions(path,['opener','read','features','predict','score'],old)
    # Row builder is the original read() AST, with only the file loader replaced by an argument.
    rd=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='read')
    rd.name='read_paragraphs'; rd.args.args[0].arg='paragraphs'
    assert isinstance(rd.body[0],ast.Assign) and isinstance(rd.body[1],ast.Assert)
    rd.body=rd.body[2:]
    loop=next(n for n in rd.body if isinstance(n,ast.For))
    assert ast.unparse(loop.iter)=='json.loads(raw)';loop.iter=ast.Name(id='paragraphs',ctx=ast.Load());ast.fix_missing_locations(rd)
    exec(compile(ast.Module(body=[rd],type_ignores=[]),str(path),'exec'),old)
    rf={'np':np};compile_functions(ROOT/'round5/round5.py',['reflow_one'],rf)
    paragraphs={s:json.loads((ROOT/'round5'/f'{s}_round5.json').read_bytes()) for s in SERIES[:2]}
    # Historical Round 5 model_paras() exactly pools eligible paragraphs, with seed as folio.
    # Reuse the original function with its ROOT pointing to archived, verified seed JSONs.
    historical={'ROOT':ROOT,'json':json};compile_functions(ROOT/'round5/round5.py',['model_paras'],historical)
    # Original function expects ROOT/r5work/generator, populated as a symlink to exact archived JSONs.
    model=historical['model_paras'](); paragraphs['Timm']=[{'folio':p['folio'],'section':p['lang'],'lines':p['words'],'source_rows':[{'physical_line':i+1} for i in range(len(p['words']))]} for p in model]
    raw_rows={s:old['read_paragraphs'](paragraphs[s]) for s in SERIES}
    for s in SERIES[:2]:
        assert raw_rows[s]==old['read'](s)
        expected=json.loads((ROOT/'predictor'/f'{s}_folds.json').read_text())
        assert {r['leaf']:r['fold'] for r in raw_rows[s]}==expected
    for s in SERIES:
        assert set(r['fold'] for r in raw_rows[s])==set(range(5))

def build_reflow(series,i):
    ps=paragraphs[series];rng=np.random.default_rng(np.random.SeedSequence([MASTER,SERIES.index(series),i]))
    inp=[{'folio':p['folio'],'lang':p['section'],'words':p['lines']} for p in ps]
    result=rf['reflow_one'](inp,rng)
    assert len(result)==len(ps)
    out=[]
    for orig,new in zip(ps,result):
        assert new['folio']==orig['folio'] and new['lang']==orig['section']
        assert [w for row in new['words'] for w in row]==[w for row in orig['lines'] for w in row]
        assert sorted(map(len,new['words']))==sorted(map(len,orig['lines']))
        out.append(dict(orig,lines=new['words']))
    rows=old['read_paragraphs'](out)
    assert [(r['folio'],r['leaf'],r['fold'],r['pos'],r['length'],r['section']) for r in rows]==[(r['folio'],r['leaf'],r['fold'],r['pos'],r['length'],r['section']) for r in raw_rows[series]]
    return rows

def predict(rows):
    return old['predict'](rows,[False,True],'target_qo',1e-3,1.0,previous_mode='qo_only')

def gain(y,p0,p1):
    ids=np.arange(len(y));return float((-np.log(p0[ids,y])+np.log(p1[ids,y])).mean())

def original(series):
    rows=raw_rows[series];y,p0,p1=predict(rows)
    return old['score'](rows,y,p0,p1,np.ones(len(rows),dtype=bool))

def replica(task):
    s,i=task; seed=f'{MASTER}:{SERIES.index(s)}:{i}'
    try:
        rows=build_reflow(s,i);g=gain(*predict(rows));assert np.isfinite(g)
        return dict(corpus=s,reflow_id=i,seed=seed,n_transitions=len(rows),gain_nats=g,status='OK',error='')
    except Exception as e:
        return dict(corpus=s,reflow_id=i,seed=seed,n_transitions='',gain_nats='',status='ERROR',error=f'{type(e).__name__}: {e}')

def h3(series):
    rows=[];ps=paragraphs[series];extras=[]
    for p in ps:
        if len(p['lines'])<4: continue
        for a,b in zip(p['lines'],p['lines'][1:]):
            if a and b: extras.append((len(a),a[-1][:2]))
    assert len(extras)==len(raw_rows[series]);rows=[dict(r,prev_token_length=n,prev_last_class=c) for r,(n,c) in zip(raw_rows[series],extras)]
    f=old['features']
    def augmented(row,add_previous,include_location):
        d=f(row,add_previous,include_location)
        d.update(prev_token_length=float(row['prev_token_length']),prev_last_class=row['prev_last_class']);return d
    old['features']=augmented
    try:
        y,p0,p1=predict(rows);return old['score'](rows,y,p0,p1,np.ones(len(rows),dtype=bool))
    finally:old['features']=f

def main():
    # Gate: remote freeze receipt is written only after GitHub confirms the commit.
    receipt=json.loads((ROOT/'remote_freeze_receipt.json').read_text());assert receipt['remote_verified'] is True
    manifest=json.loads((ROOT/'source_manifest.json').read_text());assert hashlib.sha256((ROOT/'source_manifest.json').read_bytes()).hexdigest()==receipt['manifest_sha256']
    for n,d in manifest['files'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==d,n
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==manifest['runner_sha256']
    initialize();out=ROOT/'output';out.mkdir(exist_ok=False)
    h1={s:original(s) for s in SERIES};(out/'H1.json').write_text(json.dumps(h1,indent=2)+'\n')
    # H1 must reproduce the exact original historical gain (numeric tolerance accounts for OS/Python differences).
    for s,expected in [('ZL3b',0.012038152352543678),('IT2a',0.012138546910961803)]:
        if abs(h1[s]['gain']-expected)>1e-8:raise RuntimeError(f'H1 estimator replay mismatch: {s}')
    print('H1 historical estimator replay passed; starting frozen H2',flush=True)
    h2={};h3out={};fields=['corpus','reflow_id','seed','n_transitions','gain_nats','status','error']
    with ProcessPoolExecutor(max_workers=4,initializer=initialize) as pool:
        for s in SERIES:
            results=[]
            with (out/f'{s}_G_rf.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
                for r in pool.map(replica,((s,i) for i in range(1,N+1)),chunksize=2):
                    writer.writerow(r);results.append(r)
                    if len(results)%100==0:f.flush();print(f'{s}: {len(results)}/{N}',flush=True)
            valid=[r['gain_nats'] for r in results if r['status']=='OK'];g=h1[s]['gain'];l=h1[s]['conditional_ci95'][0]
            summary={'N':N,'valid':len(valid),'invalid':N-len(valid),'G0':g,'L0':l,'H1_precision_pass':bool(l>0 and l>=.25*g)}
            if len(valid)==N:
                a=np.asarray(valid);m=float(a.mean());k=int((a>=g).sum());p=(k+1)/(N+1);summary.update(mean=m,sd=float(a.std(ddof=1)),percentiles=np.quantile(a,[.025,.975],method='linear').tolist(),k=k,p=p,rho=m/g if g!=0 else None)
                if s!='Timm' and summary['H1_precision_pass'] and m<g and p<=.05:h3out[s]=h3(s)
            h2[s]=summary;(out/'H2.json').write_text(json.dumps(h2,indent=2)+'\n')
    (out/'H3.json').write_text(json.dumps(h3out,indent=2)+'\n')
    print('DONE',flush=True)
if __name__=='__main__':main()
