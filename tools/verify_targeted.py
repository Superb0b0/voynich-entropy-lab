#!/usr/bin/env python3
"""VERIFICA MIRATA (non e' una CI completa del repository).

Replays selected attempts one by one inside a process-level sandbox and classifies each as PASS / FAIL / NON VERIFICABILE.
Reuses (read-only) hashes(), protected(), sanitize(), compare() from tools/verify_attempts.py; modifies nothing existing.

Isolation layers (an attempt must pass all):
 1. the attempt is copied OUTSIDE the repo WITHOUT results.json (it cannot copy the expected answer);
 2. new mount + network namespaces; the repository root (incl. .git, data/, HOLDOUT.md, other attempts) is hidden under an
    empty tmpfs; no network;
 3. privileges dropped (uid 65534, no capabilities, no_new_privs) AFTER the mount, so the hiding cannot be undone;
 4. strace -f audits every file/network syscall; ANY path inside the repo root or non-loopback connect is a violation
    (FAIL) even if the access did not succeed.
A mandatory self-test (negative controls that MUST fail + a positive control that MUST pass + a direct hiding probe) runs first;
if it does not behave exactly as expected, no attempt is verified (all NON VERIFICABILE)."""
import argparse, json, os, pathlib, re, shlex, shutil, subprocess, sys, tempfile
import yaml
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import verify_attempts as va  # reused read-only
PASS, FAIL, NV = "PASS", "FAIL", "NON VERIFICABILE"
LABEL = "VERIFICA MIRATA (non e' una CI completa del repository)"
FILE_CALLS = {"open","openat","openat2","stat","lstat","newfstatat","statx","access","faccessat","faccessat2","readlink","readlinkat",
              "execve","execveat","chdir","symlink","symlinkat","link","linkat","rename","renameat","renameat2","mkdir","mkdirat",
              "unlink","unlinkat","truncate","chmod","chown","utimensat","statfs","umount2","mount","getxattr","listxattr"}
LINE = re.compile(r'^(?:\[pid\s+\d+\]\s+|\d+\s+)?([a-z_0-9]+)\((.*)$')
QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"')

def hide_roots():
    roots = {str(ROOT), str(ROOT.resolve())}
    ws = os.environ.get("GITHUB_WORKSPACE")
    if ws and os.path.isdir(ws): roots |= {ws, str(pathlib.Path(ws).resolve())}
    return sorted(roots)

def parse_trace(log, cwd, roots):
    """Return list of (kind, detail). Pure function (unit-tested)."""
    out = []
    for line in log.splitlines():
        m = LINE.match(line)
        if not m: continue
        name, rest = m.group(1), m.group(2)
        if name in FILE_CALLS:
            for s in QUOTED.findall(rest):
                p = os.path.normpath(s if os.path.isabs(s) else os.path.join(cwd, s))
                for r in roots:
                    if p == r or p.startswith(r + "/") or s == r or s.startswith(r + "/"):
                        out.append(("repo_access", f"{name}: {s}")); break
        elif name == "connect" and ("AF_INET" in rest):
            a = re.search(r'inet_addr\("([^"]+)"\)', rest) or re.search(r'inet_pton\(AF_INET6, "([^"]+)"', rest)
            addr = a.group(1) if a else "?"
            if not (addr.startswith("127.") or addr == "::1"): out.append(("network", f"connect {addr}"))
    seen, uniq = set(), []
    for v in out:
        if v not in seen: seen.add(v); uniq.append(v)
    return uniq[:20]

def have_tools():
    miss = [t for t in ("strace", "unshare", "setpriv", "env", "sh") if shutil.which(t) is None]
    if os.geteuid() != 0 and shutil.which("sudo") is None: miss.append("sudo")
    return miss

INNER = r'''set -e
READY="$1"; shift
N="$1"; shift
i=0
while [ "$i" -lt "$N" ]; do mount -t tmpfs tmpfs "$1"; shift; i=$((i+1)); done
: > "$READY"
exec "$@"'''

def sandbox_cmd(workdir, argv, env, roots, ready, trace, use_strace):
    pre = [] if os.geteuid() == 0 else ["sudo", "-n"]
    envargs = ["env", "-i"] + [f"{k}={v}" for k, v in env.items()]
    tail = ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups", "--inh-caps=-all", "--bounding-set=-all", "--no-new-privs", "--"] + envargs
    if use_strace: tail += ["strace", "-f", "-qq", "-s", "4096", "-e", "trace=%file,%network", "-o", str(trace), "--"]
    return pre + ["unshare", "--mount", "--net", "--propagation", "private", "--", "sh", "-c", INNER, "sh", str(ready), str(len(roots))] + roots + tail + argv

def world(path):
    for dp, dn, fn in os.walk(path):
        os.chmod(dp, 0o777)
        for f in fn: os.chmod(os.path.join(dp, f), 0o666)

def base_env(workdir, data_dir, seed, extra=None):
    e = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(workdir), "LANG": "C.UTF-8", "PYTHONHASHSEED": str(seed),
         "VOYNICH_SEED": str(seed), "VOYNICH_DATA_DIR": str(data_dir), "VOYNICH_HOLDOUT_POLICY": "TRAIN_ONLY"}
    if extra: e.update(extra)
    return e

def verify_one(folder, data_dir, extra_env=None):
    r = dict(attempt=folder.name, outcome=NV, category="", detail="")
    def done(o, c, d): r.update(outcome=o, category=c, detail=d); return r
    cfgp = folder / "attempt.yml"
    if not cfgp.is_file(): return done(NV, "contract", "missing attempt.yml (execution contract cannot be inferred)")
    try:
        cfg = yaml.safe_load(cfgp.read_text())
        seed, tol, cmd = cfg.get("seed"), cfg.get("tolerance"), cfg.get("command")
        if not isinstance(seed, int) or isinstance(seed, bool): return done(NV, "contract", "explicit integer seed required")
        if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol < 0: return done(NV, "contract", "nonnegative tolerance required")
        if cmd is None:
            if not (folder / "run.sh").is_file(): return done(NV, "contract", "missing run.sh and command")
            cmd = ["bash", "run.sh"]
        elif isinstance(cmd, str): cmd = shlex.split(cmd)
        if not isinstance(cmd, list) or not cmd or not all(isinstance(x, str) and x for x in cmd): return done(NV, "contract", "invalid command")
    except Exception as e: return done(NV, "contract", f"invalid attempt.yml: {e}")
    exp = folder / "results.json"
    if not exp.is_file(): return done(NV, "contract", "missing committed results.json")
    miss = have_tools()
    if miss: return done(NV, "environment", "missing tools: " + ",".join(miss))
    roots = hide_roots()
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td); os.chmod(td, 0o755)  # TemporaryDirectory is 0700: the unprivileged user must be able to traverse it
        if any(str(td).startswith(x + "/") or str(td) == x for x in roots): return done(NV, "environment", "temp dir inside repo root")
        work = td / "attempt"
        shutil.copytree(folder, work, ignore=shutil.ignore_patterns("results.json", "results_ci.json", "__pycache__"))
        out = td / "shared"; out.mkdir(); trace, ready = out / "trace", out / "ready"
        world(work); os.chmod(out, 0o777)
        cmdline = sandbox_cmd(work, cmd, base_env(work, data_dir, seed, extra_env), roots, ready, trace, True)
        try: run = subprocess.run(cmdline, cwd=work, capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired: return done(NV, "timeout", "exceeded 600 s")
        if not ready.exists(): return done(NV, "environment", "sandbox could not start: " + (run.stderr or "")[-300:])
        log = trace.read_text(errors="replace") if trace.exists() else ""
        viol = parse_trace(log, str(work), roots)
        if viol: return done(FAIL, "violation", "; ".join(f"{k}:{d}" for k, d in viol[:5]))
        if run.returncode: return done(FAIL, "exit", f"command failed ({run.returncode}): {(run.stderr or '')[-300:]}")
        o = work / "results_ci.json"
        if not o.is_file(): return done(FAIL, "no_output", "no results_ci.json produced")
        try: va.compare(json.loads(exp.read_text()), json.loads(o.read_text()), tol)
        except RuntimeError as e: return done(FAIL, "replay", str(e)[:300])
        return done(PASS, "", "replay within tolerance, no isolation violation")

def probe_hidden():
    """Direct proof (no strace involved): inside the sandbox, after an attempted umount, the repo root is still empty."""
    roots = hide_roots()
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td); ready = td / "ready"; os.chmod(td, 0o777)
        script = 'for R in "$@"; do umount "$R" >/dev/null 2>&1 || true; [ -z "$(ls -A "$R" 2>/dev/null)" ] || exit 11; [ ! -e "$R/.git" ] || exit 12; done; exit 0'
        cmd = sandbox_cmd(td, ["sh", "-c", script, "sh"] + roots, {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}, roots, ready, td / "t", False)
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return ready.exists() and run.returncode == 0, f"rc={run.returncode} ready={ready.exists()} {run.stderr[-200:]}"

def _fx(body):
    return ("import os,json,subprocess,socket\nR=os.environ.get('FIXTURE_REPO_ROOT','/nonexistent')\n" + body +
            "\njson.dump({'x':1},open('results_ci.json','w'))\n")
_V = ("FAIL", "violation")
# name: (run.py, committed results.json, (expected outcome, expected category or ""))
# Every neg_* attempt would PRODUCE the expected results if isolation failed, so a PASS means a hole.
FIXTURES = {
    "pos_control_ok": (_fx("open(os.path.join(os.environ['VOYNICH_DATA_DIR'],'ZL3b-n.txt'),'rb').read(10)"), {"x": 1}, ("PASS", "")),
    "neg_direct_corpus": (_fx("open(R+'/data/ZL3b-n.txt','rb').read(10)"), {"x": 1}, _V),
    "neg_relative_corpus": (_fx("open('../../data/ZL3b-n.txt','rb').read(10)"), {"x": 1}, ("FAIL", "")),
    "neg_symlink_corpus": (_fx("os.symlink(R+'/data/ZL3b-n.txt','l.txt'); open('l.txt','rb').read(10)"), {"x": 1}, _V),
    "neg_subprocess_head": (_fx("subprocess.run(['head','-c','10',R+'/data/ZL3b-n.txt'])"), {"x": 1}, _V),
    "neg_git_show": (_fx("subprocess.run(['git','-C',R,'show','HEAD:data/ZL3b-n.txt'])"), {"x": 1}, _V),
    "neg_git_dir_env": (_fx("subprocess.run(['git','show','HEAD:data/ZL3b-n.txt'],env={'GIT_DIR':R+'/.git','PATH':os.environ['PATH']})"), {"x": 1}, _V),
    "neg_git_objects_listing": (_fx("os.listdir(R+'/.git/objects')"), {"x": 1}, _V),
    "neg_holdout_md": (_fx("open(R+'/HOLDOUT.md').read(10)"), {"x": 1}, _V),
    "neg_other_attempt_results": (_fx("open(R+'/attempts/005-refractory-qo-parameter/results.json').read(10)"), {"x": 1}, _V),
    "neg_umount_escape": (_fx("subprocess.run(['umount',R]); open(R+'/data/ZL3b-n.txt','rb').read(10)"), {"x": 1}, _V),
    "neg_network": (_fx("s=socket.socket(); s.settimeout(2); s.connect(('1.1.1.1',53))"), {"x": 1}, _V),
    "neg_copy_expected": ("import shutil\nshutil.copy('results.json','results_ci.json')  # cheating: copies the expected answer\n", {"x": 7}, ("FAIL", "")),
    "neg_wrong_results": ("import json\njson.dump({'x':2},open('results_ci.json','w'))\n", {"x": 1}, ("FAIL", "replay")),
}

def materialize(dst):
    for name, (code, res, _) in FIXTURES.items():
        d = dst / name; d.mkdir(parents=True)
        (d / "run.py").write_text(code); (d / "results.json").write_text(json.dumps(res))
        (d / "run.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\npython3 run.py\n")
        (d / "attempt.yml").write_text('seed: 1\ntolerance: 0.000001\ncommand: ["bash", "run.sh"]\n')

def selftest(data_dir):
    res = []
    ok, d = probe_hidden(); res.append(dict(name="probe_hidden_repo_and_no_umount", expected="hidden", observed="hidden" if ok else "VISIBLE", ok=ok, detail=d))
    with tempfile.TemporaryDirectory() as t:
        fx = pathlib.Path(t); os.chmod(fx, 0o755); materialize(fx)
        for name in sorted(FIXTURES):
            eo, ec = FIXTURES[name][2]
            r = verify_one(fx / name, data_dir, {"FIXTURE_REPO_ROOT": str(ROOT)})
            good = r["outcome"] == eo and (not ec or r["category"] == ec)
            res.append(dict(name=name, expected=f"{eo}/{ec or '*'}", observed=f'{r["outcome"]}/{r["category"]}', ok=good, detail=r["detail"][:160]))
    return res

def main():
    ap = argparse.ArgumentParser(description=LABEL)
    ap.add_argument("--attempts", nargs="*", default=None); ap.add_argument("--discover-min", type=int, default=5)
    ap.add_argument("--report", default="targeted-report"); ap.add_argument("--selftest-only", action="store_true")
    a = ap.parse_args()
    rep = dict(label=LABEL, scope="selected attempts only; independent replay + isolation; NOT the full repository CI", selftest=[], attempts=[], overall="")
    out = pathlib.Path(a.report); out.mkdir(parents=True, exist_ok=True)
    try:
        va.hashes(); pages = va.protected()
        names = a.attempts if a.attempts else sorted(p.name for p in (ROOT / "attempts").iterdir() if p.is_dir() and va.ATTEMPT.fullmatch(p.name) and int(p.name[:3]) >= a.discover_min)
        folders = [ROOT / "attempts" / n for n in names]
        td = tempfile.TemporaryDirectory(); data = pathlib.Path(td.name) / "data"; data.mkdir()
        for s in (ROOT / "data").glob("*.txt"):
            raw = s.read_text()
            if not re.search(r"^<f\d+[rv]\d*>\s+<!", raw, re.M): raise RuntimeError(f"{s.name}: cannot safely remove holdout pages")
            (data / s.name).write_text(va.sanitize(raw, pages))
        os.chmod(data, 0o755)
        for f in data.iterdir(): os.chmod(f, 0o644)
        os.chmod(td.name, 0o755)
    except Exception as e:
        rep["overall"] = f"NON VERIFICABILE (preflight: {e})"; write(out, rep); print(rep["overall"]); return 3
    miss = have_tools()
    if miss:
        rep["overall"] = "NON VERIFICABILE (missing tools: " + ",".join(miss) + ")"; write(out, rep); print(rep["overall"]); return 3
    rep["selftest"] = selftest(data); st_ok = all(x["ok"] for x in rep["selftest"])
    if not st_ok:
        rep["overall"] = "NON VERIFICABILE: self-test dell'isolamento NON superato - nessun attempt verificato"
        rep["attempts"] = [dict(attempt=f.name, outcome=NV, category="selftest", detail="isolation self-test failed") for f in folders]
    elif a.selftest_only: rep["overall"] = "SELF-TEST OK (nessun attempt verificato: --selftest-only)"
    else:
        rep["attempts"] = [verify_one(f, data) for f in folders]
        o = [x["outcome"] for x in rep["attempts"]]
        rep["overall"] = "FAIL" if FAIL in o else ("NON VERIFICABILE" if (NV in o or not o) else "PASS")
    write(out, rep); print(summary(rep))
    return {"PASS": 0}.get(rep["overall"], 1 if rep["overall"] == "FAIL" else 3) if not a.selftest_only or not st_ok else (0 if st_ok else 3)

def summary(rep):
    L = [f"# {LABEL}", "", f"Esito complessivo: **{rep['overall']}**", "", "## Self-test isolamento (controlli negativi/positivi)", "| controllo | atteso | osservato | ok |", "|---|---|---|---|"]
    L += [f"| {x['name']} | {x['expected']} | {x['observed']} | {'si' if x['ok'] else 'NO'} |" for x in rep["selftest"]]
    L += ["", "## Attempt (replay indipendente, uno per uno)", "| attempt | esito | categoria | dettaglio |", "|---|---|---|---|"]
    L += [f"| {x['attempt']} | {x['outcome']} | {x['category']} | {x['detail'][:140]} |" for x in rep["attempts"]]
    L += ["", "Ambito: solo gli attempt elencati; non sostituisce la CI completa. Un attempt NON VERIFICABILE non e' un attempt fallito."]
    return "\n".join(L)

def write(out, rep):
    (out / "report.json").write_text(json.dumps(rep, indent=1)); (out / "summary.md").write_text(summary(rep) + "\n")

if __name__ == "__main__":
    sys.exit(main())
