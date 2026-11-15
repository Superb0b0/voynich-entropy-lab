#!/usr/bin/env python3
"""Result-blind feasibility benchmark for attempt 014. No parameter estimates emitted."""
import ast,hashlib,os,pathlib,sys,time,random,json
ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA=pathlib.Path(os.environ["VOYNICH_DATA_DIR"])
src=ROOT/"attempts/005-refractory-qo-parameter/run.py"
tree=ast.parse(src.read_text())
cut=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="rng" for t in n.targets))
env={"__name__":"__benchmark__"}
exec(compile(ast.Module(body=tree.body[:cut],type_ignores=[]),str(src),"exec"),env)
# Use exactly one fixed bootstrap replicate (the original full paragraph sample) in each split.
groups=env["groups"]; sample=env["sample"]; mean=env["mean"]
if any(not groups[s] for s in (0,1)):sys.exit("FAIL CLOSED: empty training split")
R=200; seed=20261115
start=time.monotonic();calls=0
for fit in (0,1):
 rng=random.Random(seed+fit)
 # exact theta grid and phi grid sizes from attempt-005
 for theta in env["GRID_T"]:
  sample(fit,theta,0.0,R,rng);calls+=1
 # theta_nonqo is derived from theta grid in production; use midpoint solely for timing,
 # and do not emit or retain any parameter/result statistic.
 theta_mid=(env["GRID_T"][0]+env["GRID_T"][-1])/2
 for phi in env["GRID_P"]:
  sample(fit,theta_mid,phi,R,rng);calls+=1
elapsed=time.monotonic()-start
# Production protocol: 500 bootstrap replicates x 2 splits x (7+9) grid points.
estimated=elapsed*(500)
result={"status":"BENCHMARK_ONLY_NO_EMPIRICAL_RESULT","fit_calls":calls,"predictive_draws_per_call":R,"elapsed_seconds":round(elapsed,3),"extrapolated_full_fit_seconds":round(estimated,1),"extrapolated_full_fit_hours":round(estimated/3600,3),"note":"One full-data timing replicate per split; estimate is approximate and does not include all diagnostic/predictive overhead."}
pathlib.Path("benchmark_014.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result),flush=True)
