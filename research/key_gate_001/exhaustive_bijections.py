"""Exhaustive control family for a toy 7-to-7 monoalphabetic bijection.
This proves combinatorial completeness only for this explicitly restricted class.
It is NOT a Voynich key model and does not establish linguistic equivalence.
"""
import itertools, json, hashlib
def enumerate_bijections(symbols, outputs):
    if len(symbols)!=len(outputs) or len(set(symbols))!=len(symbols) or len(set(outputs))!=len(outputs):
        raise ValueError("alphabets must be unique and equally sized")
    for perm in itertools.permutations(outputs):
        yield dict(zip(symbols,perm))
def audit(symbols,outputs):
    keys=list(enumerate_bijections(symbols,outputs))
    tuples=[tuple(k[s] for s in symbols) for k in keys]
    n=1
    for i in range(2,len(symbols)+1): n*=i
    assert len(keys)==n and len(set(tuples))==n
    return {"class":"all bijections symbols->outputs","alphabet_size":len(symbols),
            "expected_factorial":n,"enumerated":len(keys),"unique":len(set(tuples)),
            "complete":len(keys)==n and len(set(tuples))==n,
            "sha256":hashlib.sha256(json.dumps(tuples,separators=(',',':')).encode()).hexdigest()}
if __name__=="__main__":
    print(json.dumps(audit("abcdefg","ABCDEFG"),sort_keys=True))
