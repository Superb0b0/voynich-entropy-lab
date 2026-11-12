import copy,sys,pathlib,subprocess,json,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import validate_anchor as V
H='a'*64;H2='b'*64

def base():return {'id':'ANC-0001','branch':'EXPLORATORY_ANCHOR','experiment':'ANCHOR-02','classification':'ESPLORATIVO','status':'PENDING','claim':'test','source_files':[{'filename':'report.md','canonical_id':'sha256:'+H,'sha256':H,'size_bytes':10,'origin':'Library'}],'execution':{'script_filename':None,'script_sha256':None,'command':None,'execution_date':None},'verification':{'reviewer':None,'checked_at':None,'recomputed':False,'evidence_refs':[]},'gate_effect':'NONE','evidence_level':'RIPORTATO'}
def repro(d):d['evidence_level']='RIPRODOTTO';d['execution'].update(script_filename='s.py',script_sha256=H2,command='python s.py',execution_date='2026-11-12',output_refs=['out.txt']);d['verification'].update(recomputed=True,evidence_refs=['out.txt'])
def passed(d):repro(d);d['status']='PASS';d['verification'].update(reviewer='R. Rossi',checked_at='2026-11-12T10:00:00Z')
def failed(d):d['status']='FAIL';d['failure']={'reason':'non coincide','evidence_refs':['diff.txt']}
def setv(d,path,value):
    for k in path[:-1]:d=d[k]
    d[path[-1]]=value
def drop(d,path):
    for k in path[:-1]:d=d[k]
    del d[path[-1]]
def test(name,mod,expected):
    d=base();mod(d);got=not V.validate_entry(d,FC);ok=got==expected
    print(('OK' if ok else 'ANOMALIA'),name,('VALIDA' if got else 'RIFIUTATA'))
    return not ok
def compose(*mods):return lambda d:[m(d) for m in mods]
def u(path,value):return lambda d:setv(d,path,value)
def rm(path):return lambda d:drop(d,path)
FC=V.require_formats()
T=[
('A01 base',lambda d:None,True),('A02 hash corto',u(['source_files',0,'sha256'],'deadbeef'),False),('A03 hash null',u(['source_files',0,'sha256'],None),False),('A04 hash maiuscolo',u(['source_files',0,'sha256'],'A'*64),False),('A05 gate',u(['gate_effect'],'UNLOCK'),False),('A06 classification',u(['classification'],'VALIDATO'),False),('A07 PASS senza prove',u(['status'],'PASS'),False),('A08 PASS completo',passed,True),('A09 PASS RIPORTATO',compose(passed,u(['evidence_level'],'RIPORTATO')),False),('A10 PASS senza hash script',compose(passed,u(['execution','script_sha256'],None)),False),('A11 PASS senza revisore',compose(passed,u(['verification','reviewer'],None)),False),('A12 PASS senza evidenze',compose(passed,u(['verification','evidence_refs'],[])),False),('A13 data ieri',compose(passed,u(['verification','checked_at'],'ieri')),False),('A14 RIPRODOTTO senza script',u(['evidence_level'],'RIPRODOTTO'),False),('A15 hash fittizio sintatticamente valido',passed,True),('A16 FAIL senza failure',u(['status'],'FAIL'),False),('A17 sorgente duplicata',lambda d:d['source_files'].append(copy.deepcopy(d['source_files'][0])),False),('A18 revisore spazi',compose(passed,u(['verification','reviewer'],'  ')),False),('A19 data impossibile',u(['execution','execution_date'],'2026-13-45'),False),
('B01 timestamp Z',passed,True),('B02 timestamp offset',compose(passed,u(['verification','checked_at'],'2026-11-12T10:00:00+01:00')),True),('B03 solo data',compose(passed,u(['verification','checked_at'],'2026-11-12')),False),('B04 senza fuso',compose(passed,u(['verification','checked_at'],'2026-11-12T10:00:00')),False),('B05 mese 13',compose(passed,u(['verification','checked_at'],'2026-13-12T10:00:00Z')),False),('B06 checked_at null PENDING',lambda d:None,True),
('B07 repro completo PENDING',repro,True),('B08 repro senza script',compose(repro,u(['execution','script_filename'],None)),False),('B09 repro senza hash',compose(repro,u(['execution','script_sha256'],None)),False),('B10 repro hash corto',compose(repro,u(['execution','script_sha256'],'deadbeef')),False),('B11 repro senza comando',compose(repro,u(['execution','command'],None)),False),('B12 repro comando spazi',compose(repro,u(['execution','command'],'  ')),False),('B13 repro senza data',compose(repro,u(['execution','execution_date'],None)),False),('B14 repro senza output_refs',compose(repro,rm(['execution','output_refs'])),False),('B15 repro output vuoto',compose(repro,u(['execution','output_refs'],[])),False),('B16 repro output spazi',compose(repro,u(['execution','output_refs'],[' '])),False),('B17 repro recomputed false',compose(repro,u(['verification','recomputed'],False)),False),('B18 repro evidenze vuote',compose(repro,u(['verification','evidence_refs'],[])),False),('B19 RIPORTATO vuoto',lambda d:None,True),
('B20 revisore vuoto PASS',compose(passed,u(['verification','reviewer'],'')),False),('B21 revisore whitespace PASS',compose(passed,u(['verification','reviewer'],'\t\n ')),False),('B22 revisore vuoto PENDING',u(['verification','reviewer'],''),False),('B23 revisore null PENDING',lambda d:None,True),('B24 revisore valido',passed,True),
('B25 due sorgenti',lambda d:d['source_files'].append({'filename':'x','canonical_id':'sha256:'+H2,'sha256':H2,'size_bytes':5,'origin':'Library'}),True),('B26 duplicato rinominato',lambda d:d['source_files'].append({'filename':'copia','canonical_id':'sha256:'+H,'sha256':H,'size_bytes':10,'origin':'Library'}),False),('B27 canonical incoerente',u(['source_files',0,'canonical_id'],'sha256:'+H2),False),('B28 canonical assente',rm(['source_files',0,'canonical_id']),False),('B29 canonical senza prefisso',u(['source_files',0,'canonical_id'],H),False),
('B30 FAIL completo',failed,True),('B31 FAIL senza failure',u(['status'],'FAIL'),False),('B32 FAIL motivo vuoto',compose(failed,u(['failure','reason'],'')),False),('B33 FAIL motivo spazi',compose(failed,u(['failure','reason'],'  \t')),False),('B34 FAIL senza refs',compose(failed,u(['failure','evidence_refs'],[])),False),('B35 FAIL refs spazi',compose(failed,u(['failure','evidence_refs'],[' '])),False),('B36 FAIL refs duplicati',compose(failed,u(['failure','evidence_refs'],['x','x'])),False),('B37 PENDING senza failure',lambda d:None,True),]
if __name__=='__main__':
    bad=sum(test(*t) for t in T)
    code=f"import sys;sys.modules['rfc3339_validator']=None;sys.path.insert(0,{str(ROOT)!r});import validate_anchor;validate_anchor.require_formats()"
    r=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
    good=r.returncode==2 and 'dipendenza mancante' in r.stderr
    print('C01 dependency guard',good);bad+=not good
    with tempfile.TemporaryDirectory() as t:
        for name,entry,expected in [('good.json',base(),0),('bad.json',{**base(),'status':'FAIL'},1)]:
            p=pathlib.Path(t)/name;p.write_text(json.dumps(entry));r=subprocess.run([sys.executable,str(ROOT/'validate_anchor.py'),str(p)],capture_output=True,text=True)
            good=r.returncode==expected;print('CLI',name,good);bad+=not good
    print('TOTAL',len(T)+3,'ANOMALIE',bad)
    sys.exit(bool(bad))
