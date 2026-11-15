"""Restricted synthetic bijection controls; not a Voynich decipherment test."""
import hashlib, json, math, random
def generate(symbols,outputs,count=999,seed=20261115):
    if len(symbols)!=len(outputs) or len(set(symbols))!=len(symbols) or len(set(outputs))!=len(outputs):
        raise ValueError("unique equally sized alphabets required")
    if count<1 or count>math.factorial(len(outputs)):
        raise ValueError("invalid number of distinct permutations")
    rng=random.Random(seed);seen=set();result=[]
    while len(result)<count:
        perm=list(outputs);rng.shuffle(perm);key=tuple(perm)
        if key in seen:continue
        seen.add(key);result.append(dict(zip(symbols,perm)))
    return result
def digest(result):
    return hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
if __name__=='__main__':
    result=generate('abcdefg','ABCDEFG')
    print(json.dumps({'status':'SYNTHETIC_ONLY','count':len(result),'sha256':digest(result)}))
