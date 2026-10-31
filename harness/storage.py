"""Trial records: runs/<run_id>/<task>/<model_slug>/trial-<n>/{meta,baseline,post,grade}.json + transcript.jsonl"""
import datetime as dt, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


class TrialDir:
    def __init__(self, base):
        self.path = pathlib.Path(base)
        self.path.mkdir(parents=True, exist_ok=True)
        self._t = open(self.path / "transcript.jsonl", "a")

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
