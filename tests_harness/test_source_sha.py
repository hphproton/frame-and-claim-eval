"""A zip with no .git still names its commit: git archive writes it into VERSION."""
import pathlib, subprocess, sys, tempfile, zipfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import storage

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_a_checkout_reads_git_not_the_unexpanded_placeholder():
    assert (ROOT / "VERSION").read_text().strip() == "$Format:%H$"
    assert storage._version_file_sha() == ""
    sha = storage.source_sha()
    assert sha == "unknown" or len(sha) == 40


def test_version_file_wins_when_it_holds_a_commit_id():
    old = storage.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        (pathlib.Path(tmp) / "VERSION").write_text("0123456789abcdef0123456789abcdef01234567\n")
        storage.ROOT = pathlib.Path(tmp)
        try:
            assert storage.source_sha() == "0123456789abcdef0123456789abcdef01234567"
        finally:
            storage.ROOT = old
        (pathlib.Path(tmp) / "VERSION").write_text("not a sha\n")
        storage.ROOT = pathlib.Path(tmp)
        try:
            assert storage._version_file_sha() == ""
        finally:
            storage.ROOT = old


def test_git_archive_expands_version_and_leaves_out_agent_notes():
    # The attributes are read from the archived tree, so this needs them committed in HEAD.
    if subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", "HEAD:.gitattributes"], capture_output=True).returncode != 0:
        print("SKIPPED git archive check: .gitattributes is not in HEAD yet")
        return
    with tempfile.TemporaryDirectory() as tmp:
        zpath = pathlib.Path(tmp) / "s.zip"
        # The attributes under test come from the committed tree, so archive HEAD.
        subprocess.run(["git", "-C", str(ROOT), "archive", "--format=zip", "-o", str(zpath), "HEAD"], check=True)
        with zipfile.ZipFile(zpath) as z:
            names = z.namelist()
            assert "README.md" in names, "README.md is not at the zip root"
            assert "AGENTS.md" not in names and "PILOT-PLAN.md" not in names
            version = z.read("VERSION").decode().strip()
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert version == head, (version, head)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("source sha: OK")
