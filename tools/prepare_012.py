#!/usr/bin/env python3
"""Trusted preparation step, outside the audited experiment process."""
import hashlib,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from verify_attempts import hashes,protected,sanitize,ROOT
hashes()
if len(sys.argv)!=3:sys.exit("usage: prepare_012.py OUTPUT_DIR CORPUS")
out=pathlib.Path(sys.argv[1]).resolve()
name=sys.argv[2]
if name not in ("IT2a-n.txt","ZL3b-n.txt"):sys.exit("unapproved corpus")
out.mkdir(parents=True,exist_ok=True)
data=sanitize((ROOT/"data"/name).read_text(),protected())
dest=out/name
dest.write_text(data)
digest=hashlib.sha256(dest.read_bytes()).hexdigest()
expected={"IT2a-n.txt":"a12879dfa02f8fc8f9a9c9bea5bf019283959ceca09a446abdd273baced9705c","ZL3b-n.txt":"dea09c32de148c2bbf592b00e3042993cc57d967c615159ccef458e82270cbe9"}[name]
if digest!=expected:sys.exit("FAIL CLOSED filtered SHA mismatch: "+digest)
print("Trusted preparation PASS:",name,digest)
