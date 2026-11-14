#!/usr/bin/env python3
"""Independent synthetic replay verifier. No Voynich corpus access."""
import hashlib,json,os,pathlib,subprocess,sys,tempfile,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/active_replay/fixture.py"
SEED=20261114
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verdict(reason,details=None):
    return {"status":"REPLAY_FAILED" if reason else "TECHNICAL_REPLAY_PASSED","reason":reason,"evidence":details or {}}
def verify(e):
    required=("fixture_sha256","seed","runs")
    if any(k not in e for k in required):return verdict("MISSING_EVIDENCE")
    if e["fixture_sha256"]!=digest(FIXTURE) or e["seed"]!=SEED:return verdict("INPUT_HASH_MISMATCH")
    runs=e["runs"]
    if len(runs)!=2:return verdict("MISSING_RUN")
    for i,r in enumerate(runs):
        if not all(k in r for k in ("output","output_sha256","trace","trace_sha256","returncode","command","fixture_sha256","runtime")):
            return verdict("MISSING_EVIDENCE")
        if r["returncode"]!=0:return verdict("EXECUTION_FAILED")
        if r["fixture_sha256"]!=e["fixture_sha256"]:return verdict("INPUT_HASH_MISMATCH")
        if r["command"]!=["python3","fixture.py","--seed",str(SEED),"--output","result.json"]:return verdict("PROTOCOL_MISMATCH")
        if r["output_sha256"]!=hashlib.sha256(r["output"].encode()).hexdigest():return verdict("OUTPUT_HASH_MISMATCH")
        if r["trace_sha256"]!=hashlib.sha256(r["trace"].encode()).hexdigest():return verdict("TRACE_HASH_MISMATCH")
        if not r["trace"].strip():return verdict("MISSING_ACCESS_TRACE")
        if "HOLDOUT.md" in r["trace"] or "/data/" in r["trace"]:return verdict("PROTECTED_INPUT_ACCESS")
        try:
            obj=json.loads(r["output"])
            if not (obj["count"]==64 and isinstance(obj["sum"],int) and len(obj["sha256"])==64):return verdict("INVALID_OUTPUT")
        except (ValueError,KeyError,TypeError):return verdict("INVALID_OUTPUT")
    if runs[0]["runtime"]==runs[1]["runtime"]:return verdict("SHARED_RUNTIME")
    if runs[0]["output"]!=runs[1]["output"]:return verdict("NUMERIC_TOLERANCE_EXCEEDED")
    return verdict(None,{"runs":2,"seed":SEED,"fixture_sha256":e["fixture_sha256"],"output_sha256":runs[0]["output_sha256"],"note":"Synthetic technical replay only; not scientific evidence"})
def execute():
    if shutil.which("strace") is None:raise RuntimeError("strace unavailable")
    frozen=digest(FIXTURE)
    evidence={"fixture_sha256":frozen,"seed":SEED,"runs":[]}
    with tempfile.TemporaryDirectory() as outer:
        for i in range(2):
            work=pathlib.Path(outer)/("run"+str(i))
            work.mkdir()
            shutil.copyfile(FIXTURE,work/"fixture.py")
            if digest(work/"fixture.py")!=frozen:raise RuntimeError("fixture copy mismatch")
            cmd=["python3","fixture.py","--seed",str(SEED),"--output","result.json"]
            trace=work/"access.trace"
            env={"PATH":os.environ["PATH"],"PYTHONHASHSEED":str(SEED),"HOME":str(work),"PYTHONDONTWRITEBYTECODE":"1"}
            run=subprocess.run(["strace","-f","-qq","-e","trace=file,network","-s","4096","-o",str(trace),"--",*cmd],cwd=work,env=env,capture_output=True,text=True,timeout=30)
            output=(work/"result.json").read_text() if (work/"result.json").exists() else ""
            log=trace.read_text() if trace.exists() else ""
            evidence["runs"].append({"runtime":str(work),"command":cmd,"returncode":run.returncode,"fixture_sha256":digest(work/"fixture.py"),"output":output,"output_sha256":hashlib.sha256(output.encode()).hexdigest(),"trace":log,"trace_sha256":hashlib.sha256(log.encode()).hexdigest()})
    if digest(FIXTURE)!=frozen:raise RuntimeError("fixture changed during replay")
    return evidence
def main():
    target=ROOT/"output"/"active-replay-report.json"
    target.parent.mkdir(exist_ok=True)
    try:
        e=execute()
        result=verify(e)
        (ROOT/"output"/"active-replay-evidence.json").write_text(json.dumps(e,indent=2)+"\n")
    except Exception as exc:
        result=verdict("EXECUTION_OR_EVIDENCE_ERROR",{"error":str(exc)})
    target.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"],result["reason"] or "two independent executions compared")
    return 0 if result["status"]=="TECHNICAL_REPLAY_PASSED" else 1
if __name__=="__main__":sys.exit(main())
