#!/usr/bin/env python3
"""QO-MECH-01: frozen binary Markov vs IID out-of-leaf predictive test."""
import hashlib, importlib.util, json, math, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED="bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"
spec=importlib.util.spec_from_file_location("qo_rival",ROOT/"tools/qo_rival_calibration.py")
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

def fold(page):
    leaf=int(page[1:].split("r")[0].split("v")[0])
    return int(hashlib.sha256(("QO-MECH-01:"+str(leaf)).encode()).hexdigest(),16)%2

def pairs(groups):
    out={0:[],1:[]}
    for (page,para),seq in groups.items():
        seq=sorted(seq)
        for (i,a),(j,b) in zip(seq,seq[1:]):
            if j==i+1:out[fold(page)].append((int(a.startswith("qo")),int(b.startswith("qo"))))
    return out

def model(train):
    n=len(train)
    next_q=sum(y for x,y in train)
    iid=(next_q+1)/(n+2)
    conditional=[]
    for prev in (0,1):
        subset=[y for x,y in train if x==prev]
        conditional.append((sum(subset)+1)/(len(subset)+2))
    return iid,conditional

def logloss(test,pred):
    return -sum(math.log(pred[x] if y else 1-pred[x]) for x,y in test)/len(test)

def run():
    if (ROOT/"HOLDOUT.md").exists() or (ROOT/"data"/"ZL3b-n.txt").exists():
        raise RuntimeError("Protected or original inputs present in analysis workspace")
    safe=ROOT/"training-snapshot"/"data"/"ZL3b-n.txt"
    manifest=json.loads((ROOT/"training-snapshot"/"report"/"input-manifest.json").read_text())
    raw=safe.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if manifest.get("original_sha256")!=EXPECTED or manifest.get("training_sha256")!=digest:
        raise RuntimeError("training SHA provenance mismatch")
    q.SOURCE,q.SHA=safe,digest
    groups=q.parse()
    byfold=pairs(groups)
    result={"protocol":"research/qo-mech-01-protocol.md","status":"EXPLORATORY_NOT_VALIDATED",
            "original_sha256":EXPECTED,"training_sha256":digest,"threshold_nats":0.005,"directions":{}}
    eligible=True; supported=True
    for source,target in ((0,1),(1,0)):
        train,test=byfold[source],byfold[target]
        qo_pre=sum(x for x,y in test)
        if not train or not test or qo_pre<30:
            eligible=False
            result["directions"][f"{source}_to_{target}"]={"eligible":False,"train_pairs":len(train),"test_pairs":len(test),"qo_predecessors":qo_pre}
            continue
        iid,cond=model(train)
        iid_loss=logloss(test,[iid,iid])
        markov_loss=logloss(test,cond)
        delta=iid_loss-markov_loss
        supported=supported and delta>=0.005
        result["directions"][f"{source}_to_{target}"]={
            "eligible":True,"train_pairs":len(train),"test_pairs":len(test),
            "qo_predecessors":qo_pre,"observed_qo_to_qo":sum(x*y for x,y in test),
            "observed_qo_to_qo_rate":sum(x*y for x,y in test)/qo_pre,
            "iid_p_next_qo":iid,"markov_p_next_qo_given_prev_0":cond[0],
            "markov_p_next_qo_given_prev_1":cond[1],
            "iid_predicted_qo_to_qo":qo_pre*iid,
            "markov_predicted_qo_to_qo":qo_pre*cond[1],
            "iid_log_loss_nats":iid_loss,"markov_log_loss_nats":markov_loss,
            "delta_nats_per_pair":delta}
    result["verdict"]="eseguito: inconclusivo" if not eligible else ("eseguito: confermato" if supported else "eseguito: falsificato")
    result["verdict_scope"]="QO-MECH-01 binary first-order Markov predictive advantage only; no Voynich decipherment"
    return result

def main():
    first=run();second=run()
    a=json.dumps(first,sort_keys=True,indent=2)+"\n"
    b=json.dumps(second,sort_keys=True,indent=2)+"\n"
    if a!=b:raise RuntimeError("non-deterministic replay")
    out=ROOT/"research-output";out.mkdir(exist_ok=True)
    (out/"qo-mech-01.json").write_text(a)
    print(a)

if __name__=="__main__":main()
