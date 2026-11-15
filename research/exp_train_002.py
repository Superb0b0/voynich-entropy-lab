#!/usr/bin/env python3
"""EXP-TRAIN-002 preregistered paragraph-preserving null. Aggregate output only."""
import hashlib, importlib.util, json, pathlib, random, tempfile
from collections import defaultdict
from exp_train_001 import ROOT, SOURCE, PARSER, EXPECTED, PARSER_SHA, protected, filter_pages, require, jaccard

def statistic(paragraphs):
    total=0.; pairs=0
    for lines in paragraphs:
        for a,b in zip(lines,lines[1:]):
            total+=jaccard(a,b); pairs+=1
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
        path=pathlib.Path(td)/"training.txt"
        path.write_text(filtered,encoding="utf-8")
        spec=importlib.util.spec_from_file_location("locked_parser",PARSER)
        parser=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        records=parser.parse_corpus(path,verify_source=False)["records"]
        require(records)
        source_lines=filtered.splitlines()
        by_page=defaultdict(list)
        for rec in records:
            require(rec["folio"] not in forbidden)
            by_page[rec["folio"]].append(rec)
        paragraphs=[]
        for folio,rows in sorted(by_page.items()):
            current=[]
            for i,rec in enumerate(rows):
                if i==0 or "<%>" in source_lines[rec["physical_line"]-1]:
                    if len(current)>=3: paragraphs.append(current)
                    current=[]
                tokens=[t for t in rec["tokens"] if len(t)>=3 and t.isascii() and t.isalpha()]
                if len(tokens)>=2:
                    current.append(frozenset(t[:3] for t in tokens))
            if len(current)>=3: paragraphs.append(current)
        require(paragraphs)
        observed,pairs=statistic(paragraphs)
        rng=random.Random(20261116)
        null=[]
        for _ in range(999):
            shuffled=[]
            for lines in paragraphs:
                order=list(lines);rng.shuffle(order);shuffled.append(order)
            null.append(statistic(shuffled)[0])
        mean=sum(null)/len(null)
        p=(1+sum(v>=observed for v in null))/1000
        print(json.dumps({"experiment":"EXP-TRAIN-002","training_only":True,
              "status":"EXPLORATORY","eligible_paragraphs":len(paragraphs),
              "adjacent_pairs":pairs,"observed":round(observed,9),
              "null_mean":round(mean,9),"observed_minus_null":round(observed-mean,9),
              "p_one_sided":p,"permutations":999,"seed":20261116,
              "verdict":"SURVIVES_PARAGRAPH_CONTROL" if p<=0.01 and observed>mean else "NOT_SUPPORTED_UNDER_PARAGRAPH_CONTROL"},sort_keys=True))
if __name__=="__main__":
    try:main()
    except Exception:
        print("EXP-TRAIN-002 FAIL CLOSED")
        raise SystemExit(1)
