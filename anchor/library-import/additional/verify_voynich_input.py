from pathlib import Path
import hashlib
p=Path('/mnt/data/ZL3b-n(7).txt')
if not p.is_file():
    print('MISSING',p)
    raise SystemExit(2)
h=hashlib.sha256(p.read_bytes()).hexdigest()
print('input_path:',p)
print('bytes:',p.stat().st_size)
print('sha256:',h)
print('prefix_ok:',h.startswith('bf5b6d4a'))
print('suffix_ok:',h.endswith('ccafc'))
print('script_sha256:',hashlib.sha256(Path(__file__).read_bytes()).hexdigest())