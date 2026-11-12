#!/usr/bin/env python3
"""Validazione fail-closed: schema, formati, coerenza identificativi; NON verifica byte sorgenti."""
import json,sys,pathlib
SCHEMA=pathlib.Path(__file__).with_name('anchor_entry.schema.json')
def fatal(message):
    print('ERRORE: '+message,file=sys.stderr)
    raise SystemExit(2)
def require_formats():
    try:
        import rfc3339_validator
        from jsonschema import FormatChecker
    except ImportError as e: fatal(f'dipendenza mancante ({e.name}); installare requirements.txt')
    fc=FormatChecker()
    for f,bad in [('date','2026-13-45'),('date-time','ieri'),('date-time','2026-11-12T10:00:00')]:
        if f not in fc.checkers: fatal(f'formato {f} non controllato')
        try: fc.check(bad,f)
        except Exception: pass
        else: fatal(f'formato {f} accetta valore invalido: {bad}')
    return fc
def semantic_errors(entry):
    errs=[]; seen=set()
    for i,f in enumerate(entry.get('source_files',[])):
        if not isinstance(f,dict): continue
        sha=f.get('sha256'); cid=f.get('canonical_id')
        if isinstance(sha,str) and cid!=f'sha256:{sha}':errs.append(f'source_files[{i}]: canonical_id non coincide con sha256')
        if isinstance(cid,str):
            if cid in seen: errs.append(f'source_files[{i}]: duplicato {cid}')
            seen.add(cid)
    return errs
def validate_entry(entry,fc=None):
    from jsonschema import Draft202012Validator
    fc=fc if fc is not None else require_formats()
    schema=json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema,format_checker=fc)
    errs=[f"{'/'.join(map(str,e.absolute_path)) or '<root>'}: {e.message}" for e in validator.iter_errors(entry)]
    return errs+semantic_errors(entry)
def main(paths):
    fc=require_formats();bad=False;ids=set()
    for path in paths:
        try: entry=json.loads(pathlib.Path(path).read_text(encoding='utf8'))
        except (OSError,ValueError) as e: fatal(f'input non leggibile: {e}')
        errs=validate_entry(entry,fc)
        if entry.get('id') in ids:errs.append('id duplicato nel batch')
        ids.add(entry.get('id'))
        print(('RIFIUTATA' if errs else 'VALIDA'),path)
        for e in errs:print(' -',e)
        bad |= bool(errs)
    return int(bad)
if __name__=='__main__':
    if len(sys.argv)<2:fatal('uso: validate_anchor.py voce.json [...]')
    sys.exit(main(sys.argv[1:]))
