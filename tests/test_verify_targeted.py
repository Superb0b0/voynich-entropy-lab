import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import verify_targeted as vt
R = ["/work/repo"]
class TraceParser(unittest.TestCase):
    def test_repo_git_access(self): self.assertTrue(vt.parse_trace('12 openat(AT_FDCWD, "/work/repo/.git/HEAD", O_RDONLY) = -1 ENOENT\n', "/t/a", R))
    def test_git_argv(self): self.assertTrue(vt.parse_trace('7 execve("/usr/bin/git", ["git", "-C", "/work/repo", "show"], 0x0 /* 3 vars */) = 0\n', "/t/a", R))
    def test_alias_prefix_not_matched(self): self.assertFalse(vt.parse_trace('1 openat(AT_FDCWD, "/work/repository/x", O_RDONLY) = 3\n', "/t/a", R))
    def test_relative_path_resolves_from_cwd(self): self.assertTrue(vt.parse_trace('1 openat(AT_FDCWD, "../repo/data/x", O_RDONLY) = 3\n', "/work/a", R))
    def test_external_connect(self): self.assertTrue(vt.parse_trace('1 connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("1.1.1.1")}, 16) = -1\n', "/t", R))
    def test_loopback_allowed(self): self.assertFalse(vt.parse_trace('1 connect(3, {sa_family=AF_INET, sin_port=htons(53), sin_addr=inet_addr("127.0.0.1")}, 16) = 0\n', "/t", R))
    def test_data_dir_allowed(self): self.assertFalse(vt.parse_trace('1 openat(AT_FDCWD, "/tmp/x/data/ZL3b-n.txt", O_RDONLY) = 3\n', "/t", R))
if __name__ == "__main__": unittest.main()
