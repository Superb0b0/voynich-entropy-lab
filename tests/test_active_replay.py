import copy,hashlib,unittest
from scripts.active_replay import verify,verdict,SEED,FIXTURE,digest
class ReplayNegativeTests(unittest.TestCase):
    def setUp(self):
        out='{"count":64,"sum":1,"sha256":"'+'0'*64+'"}'
        trace='openat(AT_FDCWD, "fixture.py", O_RDONLY) = 3'
        run={"runtime":"a","command":["python3","fixture.py","--seed",str(SEED),"--output","result.json"],"returncode":0,"fixture_sha256":digest(FIXTURE),"output":out,"output_sha256":hashlib.sha256(out.encode()).hexdigest(),"trace":trace,"trace_sha256":hashlib.sha256(trace.encode()).hexdigest()}
        other=copy.deepcopy(run);other["runtime"]="b"
        self.e={"fixture_sha256":digest(FIXTURE),"seed":SEED,"runs":[run,other]}
    def test_two_runs(self):self.assertEqual(verify(self.e)["status"],"TECHNICAL_REPLAY_PASSED")
    def test_missing_trace(self):
        del self.e["runs"][0]["trace"]
        self.assertEqual(verify(self.e)["reason"],"MISSING_EVIDENCE")
    def test_modified_hash(self):
        self.e["runs"][0]["output_sha256"]="0"*64
        self.assertEqual(verify(self.e)["reason"],"OUTPUT_HASH_MISMATCH")
    def test_shared_runtime(self):
        self.e["runs"][1]["runtime"]="a"
        self.assertEqual(verify(self.e)["reason"],"SHARED_RUNTIME")
    def test_protected_access(self):
        self.e["runs"][0]["trace"]+='\\nopenat(AT_FDCWD, "HOLDOUT.md", O_RDONLY) = -1'
        self.e["runs"][0]["trace_sha256"]=hashlib.sha256(self.e["runs"][0]["trace"].encode()).hexdigest()
        self.assertEqual(verify(self.e)["reason"],"PROTECTED_INPUT_ACCESS")
    def test_divergent_output(self):
        self.e["runs"][1]["output"]='{"count":64,"sum":2,"sha256":"'+'0'*64+'"}'
        self.e["runs"][1]["output_sha256"]=hashlib.sha256(self.e["runs"][1]["output"].encode()).hexdigest()
        self.assertEqual(verify(self.e)["reason"],"NUMERIC_TOLERANCE_EXCEEDED")
if __name__=="__main__":unittest.main()
