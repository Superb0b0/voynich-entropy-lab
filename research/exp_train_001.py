#!/usr/bin/env python3
"""EXP-TRAIN-001. Never log protected identifiers, page labels or training text."""
import ast, hashlib, importlib.util, json, pathlib, random, re, tempfile
from collections import defaultdict

ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/ZL3b-n.txt"
PARSER=ROOT/"experiments/line-memory/experiment/inputs/ivtff_parser_rc1_2.py"
EXPECTED="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
PARSER_SHA="8a614436a2d5dc3cb30c282743929aaa21a379d9da7e691b4277c670ce2a91c5"
PAGE=re.compile(r"^<(f[0-9]+[rv][0-9]*)>\s+<!")
HOLD=re.compile(r"(?m)^- pagine riservate \((\d+)\):\s*(\[[^\n]*\])")

def require(ok):
    if not ok: raise RuntimeError("fail-closed validation")

def protected():
    m=HOLD.search((ROOT/"HOLDOUT.md").read_text())
    require(m is not None)
    a=ast.literal_eval(m.group(2))
    require(isinstance(a,list) and len(a)==int(m.group(1)) and len(set(a))==len(a) and len(a)>0)
    require(all(isinstance(x,str) and re.fullmatch(r"f[0-9]+[rv][0-9]*",x) for x in a))
    return set(a)

def filter_pages(raw, forbidden):
    out=[]; current=None; seen=set(); removed=set()
    for line in raw.splitlines(keepends=True):
        m=PAGE.match(line)
        if m:
            current=m.group(1)
            require(current not in seen)
            seen.add(current)
        if current in forbidden:
            removed.add(current)
        else: out.append(line)
    require(forbidden.issubset(seen) and removed==forbidden)
    filtered="".join(out)
    require(not any(PAGE.match(line) and PAGE.match(line).group(1) in forbidden for line in filtered.splitlines()))
    return filtered

def jaccard(a,b):
    return len(a & b)/len(a | b)

def statistic(pages):
    total=0.0; pairs=0
    for lines in pages:
        for a,b in zip(lines,lines[1:]):
            total+=jaccard(a,b)
            pairs+=1
    require(pairs>0)
    return total/pairs,pairs

def main():
    raw=SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==EXPECTED)
    require(hashlib.sha256(PARSER.read_bytes()).hexdigest()==PARSER_SHA)
    forbidden=protected()
    filtered=filter_pages(raw.decode("utf-8"),forbidden)
    require(hashlib.sha256(filtered.encode()).hexdigest()!=EXPECTED)
    with tempfile.TemporaryDirectory() as td:
        p=pathlib.Path(td)/"training.txt"
        p.write_text(filtered,encoding="utf-8")
        spec=importlib.util.spec_from_file_location("locked_parser",PARSER)
        parser=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        records=parser.parse_corpus(p,verify_source=False)["records"]
        require(records)
        by_page=defaultdict(list)
        for rec in records:
            require(rec["folio"] not in forbidden)
            tokens=[t for t in rec["tokens"] if len(t)>=3 and t.isascii() and t.isalpha()]
            if len(tokens)>=2: by_page[rec["folio"]].append(frozenset(t[:3] for t in tokens))
        pages=[v for _,v in sorted(by_page.items()) if len(v)>=3]
        require(len(pages)>0)
        observed,pairs=statistic(pages)
        rng=random.Random(20261115)
        null=[]
        for _ in range(999):
            shuffled=[]
            for lines in pages:
                order=list(lines)
                rng.shuffle(order)
                shuffled.append(order)
            null.append(statistic(shuffled)[0])
        pvalue=(1+sum(x>=observed for x in null))/1000
        result={"experiment":"EXP-TRAIN-001","status":"EXPLORATORY","training_only":True,
                "eligible_pages":len(pages),"adjacent_pairs":pairs,
                "observed":round(observed,9),"null_mean":round(sum(null)/len(null),9),
                "observed_minus_null":round(observed-sum(null)/len(null),9),
                "p_one_sided":pvalue,"permutations":999,"seed":20261115,
                "verdict":"EXPLORATORY_SUPPORT" if pvalue<=0.01 else "NOT_SUPPORTED"}
        print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    try: main()
    except Exception:
        # Never include exception text; parser errors can contain protected identifiers.
        print('EXP-TRAIN-001 FAIL CLOSED')
        raise SystemExit(1)
