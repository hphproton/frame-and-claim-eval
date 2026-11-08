"""Trial records: runs/<run_id>/<task>/<model_slug>/trial-<n>/{meta,baseline,post,grade}.json + transcript.jsonl"""
import datetime as dt, hashlib, json, pathlib, re, tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def source_sha():
    """HEAD when this process started the command. A later commit of the output is a child of this SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _sha256_file(path):
    try:
        return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def spec_stamp(task_dir):
    """What the model was held to, fixed at trial start and written into meta.json.

    spec_version is the number the task's collect.py stamps into every post
    (1 when it stamps none); a judge keeps the older behaviour for older posts.
    instruction_text_rev counts wording-only edits of instruction.md and is kept
    in the task's harness.toml, so a clarification does not change spec_version.
    The hashes pin the exact instruction text and the judge and collector code.
    """
    task_dir = pathlib.Path(task_dir)
    tests = task_dir / "tests"
    version = 1
    try:
        found = re.search(r'\["spec_version"\]\s*=\s*(\d+)', (tests / "collect.py").read_text())
        if found:
            version = int(found.group(1))
    except OSError:
        pass
    try:
        rev = int(tomllib.loads((task_dir / "harness.toml").read_text()).get("instruction_text_rev", 1))
    except (OSError, ValueError):
        rev = 1
    combined = hashlib.sha256()
    if tests.is_dir():
        for path in sorted(p for p in tests.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
            combined.update(str(path.relative_to(tests)).encode() + b"\0" + path.read_bytes() + b"\0")
    return {
        "spec_version": version,
        "instruction_text_rev": rev,
        "instruction_sha256": _sha256_file(task_dir / "instruction.md"),
        "judge_sha256": _sha256_file(tests / "judge.py"),
        "tests_sha256": combined.hexdigest(),
    }


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


class TrialDir:
    def __init__(self, base):
        self.path = pathlib.Path(base)
        self.path.mkdir(parents=True, exist_ok=True)
        # Replace, do not append. A second run into the same trial directory must not
        # leave the previous tool events in front of the new ones (replay re-executes every tool event).
        self._t = open(self.path / "transcript.jsonl", "w")

    @classmethod
    def for_trial(cls, run_id, task_id, model_label, trial):
        return cls(RUNS / run_id / task_id / slug(model_label) / f"trial-{trial}")

    def event(self, kind, **data):
        self._t.write(json.dumps({"t": utc_now(), "type": kind, **data}) + "\n")
        self._t.flush()

    def save(self, name, obj):
        (self.path / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

    def close(self):
        self._t.close()
