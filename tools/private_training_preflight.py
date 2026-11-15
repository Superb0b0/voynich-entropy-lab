#!/usr/bin/env python3
"""Private holdout isolation preflight. Never emits protected IDs or training bytes."""
import ast, hashlib, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def stop(msg):
    print("FAIL CLOSED: "+msg, file=sys.stderr); sys.exit(1)
def main():
    raw=(ROOT/"data/ZL3b-n.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest()!="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc": stop("corpus checksum")
    h=(ROOT/"HOLDOUT.md").read_text()
    m=re.search(r"(?m)^- pagine riservate \(\d+\):\s*(\[[^\n]*\])",h)
    if not m: stop("protected pages not machine-readable")
    try: ids=ast.literal_eval(m.group(2))
    except (SyntaxError,ValueError): stop("protected pages syntax")
    if not isinstance(ids,list) or len(ids)!=int(m.group(1)) or not ids or not all(isinstance(x,str) and re.fullmatch(r"f\d+[rv]\d*",x) for x in ids): stop("protected pages invalid")
    protected=set(ids)
    if len(protected)!=len(ids): stop("duplicate protected pages")
    pages=re.findall(r"(?m)^<(f\d+[rv]\d*)>\s+<!",raw.decode("utf-8"))
    if not pages or not protected.issubset(set(pages)): stop("protected page missing from corpus")
    if len(pages)!=len(set(pages)): stop("duplicate page headers")
    # Do not export training bytes or its digest from a public repository.
    print("PASS: corpus hash; holdout format; protected pages exist; page headers unique")
    print("TRAINING EXPORT: DISABLED ON PUBLIC RUNNERS")
if __name__=="__main__": main()
