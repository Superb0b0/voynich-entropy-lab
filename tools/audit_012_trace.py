#!/usr/bin/env python3
"""Audit traced file opens for original corpus and HOLDOUT; fail closed."""
import pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
trace=pathlib.Path(sys.argv[1]).read_text(errors="replace")
for line in trace.splitlines():
 if not re.search(r"\b(open|openat|openat2|readlink|readlinkat)\(",line):continue
 for raw in re.findall(r'"([^"\n]+)"',line):
  path=pathlib.Path(raw)
  if not path.is_absolute():path=root/path
  path=path.resolve()
  if path==root/"HOLDOUT.md" or path.parent==root/"data" and path.suffix==".txt":
   sys.exit("FAIL CLOSED: experiment opened forbidden input: "+str(path))
print("strace input isolation PASS")
