import hashlib,json,random
seed=20261113
rng=random.Random(seed)
# Known-mechanism calibration: detect alternating binary generator via lag-1 agreement.
def score(xs): return sum(a==b for a,b in zip(xs,xs[1:]))/(len(xs)-1)
n=200
alternating=[i%2 for i in range(n)]
iid=[rng.randrange(2) for _ in range(n)]
result={'seed':seed,'n':n,'alternating_agreement':score(alternating),'iid_agreement':score(iid),'criterion':'alternating <= 0.10; iid 0.35..0.65','passed':score(alternating)<=.1 and .35<=score(iid)<=.65}
print(json.dumps(result,sort_keys=True))
