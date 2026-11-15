#!/usr/bin/env python3
"""Attempt 007 CI reproduction. Regenerates 30 texts and fails on SHA mismatch."""
import hashlib,json,math,pathlib,random,re,statistics,subprocess,sys,urllib.request,zipfile,io
EXPECTED="""a705e4dc7a65ed3adff6173ac0f297ef30302c1eae1b2c66a745c3f89ae43e04
be74d7adabf35dda9a7e0fe225d1330c089510bdaa83f6912012ce40d3c4bfe0
4bdb57a707403d72ede8df69175a216e090900b79b4db08101aee766d6c11cdb
6d8a8eb5cb876634868943e6c1c16cdda28860a493151197091dc90646ec3f39
82f97c3febfa56626c21cbdc2390114c07d8f0003416396c718737d20c6af785
e45f452f10e3b071bf3950c26a717975cc80c2788435133df5d63e371fd583c7
c25318035969991a8a12de74a08106d0de8be486d91742d8962218350fbaeb6e
7f2eb2d4ec3a6e2c6f0b6447628843f99e8767d9b6128f0641fe23295b68c5bc
0316f3d65902a3a3755878d08682db385c200f3343d7b9693f997044b885537e
190c8c192934294b4721af1104712f1876fae5e2ce8312a2d4a1ef631ff22101
04078c7a028f3d5558f92aa656c01e2e870bd72fd9c26730c27a121bf98aa878
6b1a36280bc640256f98deb7cd284c16840ef4699551bf521e1bd8ca845e5911
d22b16d15b1a75533a6326b3df655af95c4934bae0b2e192fe37bc151276e16d
e6a1438a7bcf4668d08ee4fb964eb4046e4ac3f7607ad6174810a763a9c592b1
adc6351242490ed03deb9a21aeaea4991d8fa84be512d2961d558d3d4678d88d
27a4c9f0e29b907da883db4ce803cd81f985f12a3fd5b498aa90ea4c9f4e84d3
4ebf257f09f126d9f31a863f5c0e703a0373cdcfe285aeb8c4b29d1b97642fbd
e3bdc9db80e5977709df64b6858f7b3dcc300ad4a29f06bb864e30ee5e8fdc4c
a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956
48061c4d2ce35149406444269d880494e751cc8ca2e849d5d0f8f42ed87306cf
15b74bed2d4ec04f10a30821742c107500819bb3ab12e0887014483bbf08755d
aec3c6a1ffaaf5b00441c5ba7815cb8e51c60f2366cc9bcf0aea6d15e4198fdf
93bc910e516b912e5485b560a2b635173147bd5b0ff15afbd3a450d89e5813e6
697882af8b2a34d4541f9000a40e07a6ee7b83843c210357553a1761aba6ed2d
ea1084114e9810c23e885ebf559f3fc1e7bcc4fe43dcac6552711ea90a3e6713
865331745aa53e84cdaca22c5b31f5348b710b0190c1d79e9c7d20b7a4df2ff1
207b29c6107b143425568c03fbfc3ccee83f0d57eec3da20ca516a38a047efb7
a952f54c5ea581de3a375debcf9940fcfe9e79233aab37a38a2096767f976d73
ca752c94e79d4c139ef239b764a4c1ed2fce709d2b823ce631481d32309eac9e
499f64c9c5d5de40ef7108c768a3661d1055992337c2ce543c37dc463e3a15ac""".splitlines()
ROOT=pathlib.Path("ts007-work");ROOT.mkdir(exist_ok=True)
url="https://github.com/TorstenTimm/SelfCitationTextgenerator/archive/refs/heads/master.zip"
print("Downloading original Java generator",flush=True)
with urllib.request.urlopen(url,timeout=120) as resp: blob=resp.read()
print("generator_zip_sha256",hashlib.sha256(blob).hexdigest(),flush=True)
with zipfile.ZipFile(io.BytesIO(blob)) as z:
 for info in z.infolist():
  dest=(ROOT/info.filename).resolve()
  if not dest.is_relative_to(ROOT.resolve()):raise RuntimeError("ZIP traversal")
 z.extractall(ROOT)
repo=ROOT/"SelfCitationTextgenerator-master"
src=sorted((repo/"source/src/main/java").rglob("*.java"))
assert len(src)==35,len(src)
classes=ROOT.resolve()/"classes";classes.mkdir(exist_ok=True)
subprocess.run(["javac","-encoding","UTF-8","-d",str(classes)]+[str(x) for x in src],check=True,timeout=180)
config=(repo/"executable/conf.properties").read_text()
assert config.count("method.random.pseudo.seed=")==1
CL=["qo","ch","sh","d","o","y","s"]
def cl(w):return next((i for i,c in enumerate(CL) if w.startswith(c)),7)
def counts(pg):
 c=[cl(w) for w in pg]
 return [sum(c[i]==c[i+1] for i in range(len(pg)-1)),sum(c[i]==c[i+1]==0 for i in range(len(pg)-1)),sum(pg[i]==pg[i+1] for i in range(len(pg)-1))]
out=[]
for seed,expected in enumerate(EXPECTED,1):
 work=ROOT/f"seed_{seed:02}";work.mkdir();(work/"generate").mkdir()
 new,n=re.subn(r"(?m)^(method\.random\.pseudo\.seed=)\S+",lambda m:m[1]+str(seed),config)
 assert n==1
 (work/"conf.properties").write_text(new)
 subprocess.run(["java","-cp",str(classes),"de.voynich.text.SelfCitationTextGenerator"],cwd=work,check=True,stdout=subprocess.DEVNULL,timeout=120)
 p=work/"generate/generated_text.txt";raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 if sha!=expected:raise RuntimeError(f"seed {seed} hash mismatch {sha} != {expected}")
 lines=[s for s in raw.decode().splitlines() if s and not s.startswith("#")]
 assert len(lines)==1200,(seed,len(lines))
 words=[re.sub("[^a-z]","",s.split()[0].lower()) for s in lines]
 assert all(words)
 pages=[words[i:i+29] for i in range(0,len(words),29)]
 obs=[sum(counts(pg)[j] for pg in pages) for j in range(3)]
 rng=random.Random(20261121+seed);null=[0,0,0]
 for _ in range(1000):
  for pg in pages:
   shuffled=pg.copy();rng.shuffle(shuffled);v=counts(shuffled)
   for j in range(3):null[j]+=v[j]
 exp=[x/1000 for x in null]
 if any(e==0 for e in exp):raise RuntimeError(f"null expected zero seed {seed}")
 ratios=[round(o/e,8) for o,e in zip(obs,exp)]
 out.append(dict(seed=seed,sha256=sha,pages=len(pages),lines=len(lines),observed=obs,expected=exp,ratios=ratios))
 print("seed",seed,"SHA256 MATCH",flush=True)
a=sorted(x["ratios"][0] for x in out);q=sorted(x["ratios"][1] for x in out)
pos=.05*(len(a)-1);i=int(pos);pct=a[i]+(a[i+1]-a[i])*(pos-i)
med=statistics.median(q)
report=dict(status="CI_REPRODUCED_007_METRICS",n=len(out),same_class_oe_percentile_5=pct,qoqo_oe_median=med,reject=pct>.75 and med>.5,seeds=out)
pathlib.Path("results_ci_007.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="seeds"},indent=2),flush=True)
