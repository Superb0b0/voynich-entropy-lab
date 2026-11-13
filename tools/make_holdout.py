#!/usr/bin/env python3
import re, sys, random, hashlib, collections

SEED = 20261114          # fissato dall'utente, non modificare
FRACTION = 0.20
CORPUS = "data/ZL3b-n.txt"

raw = open(CORPUS, "rb").read()
corpus_sha = hashlib.sha256(raw).hexdigest()
text = raw.decode("utf-8", errors="replace")

page_re = re.compile(r"^<(f\d+[rv]\d*)>\s+<!\s*(.*?)>", re.M)
leaf_re = re.compile(r"^f(\d+)")
lang_re = re.compile(r"\$L=([A-Za-z])")

leaves = collections.defaultdict(lambda: {"pages": [], "langs": []})
for m in page_re.finditer(text):
    page, attrs = m.group(1), m.group(2)
    leaf = int(leaf_re.match(page).group(1))
    leaves[leaf]["pages"].append(page)
    lm = lang_re.search(attrs)
    leaves[leaf]["langs"].append(lm.group(1) if lm else "?")

if not leaves:
    sys.exit("ERRORE: nessuna intestazione di pagina riconosciuta. Non procedere.")

def stratum(langs):
    c = collections.Counter(l for l in langs if l in "AB")
    return c.most_common(1)[0][0] if c else "other"

strata = collections.defaultdict(list)
for leaf, d in sorted(leaves.items()):
    strata[stratum(d["langs"])].append(leaf)

rng = random.Random(SEED)
held = []
for s in sorted(strata):
    members = strata[s]
    k = max(1, round(len(members) * FRACTION))
    held += rng.sample(members, k)
held = sorted(held)

pages = [p for l in held for p in leaves[l]["pages"]]
digest = hashlib.sha256(",".join(map(str, held)).encode()).hexdigest()

with open("HOLDOUT.md", "w") as f:
    f.write("# HOLDOUT (NON APRIRE senza autorizzazione dell'utente)\n\n")
    f.write(f"- seme: {SEED}\n- frazione: {FRACTION}\n- corpus: {CORPUS}\n- SHA-256 corpus: {corpus_sha}\n")
    f.write(f"- strati (fogli): " + ", ".join(f"{s}={len(v)}" for s, v in sorted(strata.items())) + "\n")
    f.write(f"- fogli riservati ({len(held)}): {held}\n")
    f.write(f"- pagine riservate ({len(pages)}): {pages}\n")
    f.write(f"- SHA-256 elenco fogli: {digest}\n")
print("fogli totali:", len(leaves), "riservati:", len(held), "pagine:", len(pages))
