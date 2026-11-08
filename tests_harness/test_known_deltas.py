"""results/known-deltas.json explains differences; it must not hide any."""
import contextlib, io, json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import known_deltas as kd
from harness.replay import replay_agrees, replay_deltas


def entry(**over):
    base = {"check": "replay", "run": "r", "task": "t", "model": "m", "trial": "trial-1",
            "field": "goal", "saved": True, "observed": False, "cause": "other",
            "evidence": "tests_harness/test_known_deltas.py", "added_in": "abc1234"}
    base.update(over)
    return base


def seen(**over):
    item = entry(**over)
    for key in ("check", "cause", "evidence", "added_in"):
        item.pop(key)
    return item


def run(observed, entries, check="replay"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        counts = kd.report(check, observed, entries)
    return counts, buf.getvalue()


# Exact match passes, and both lists are printed.
counts, out = run([seen()], [entry()])
assert counts == (0, 0), counts
assert "KNOWN" in out and "UNEXPLAINED" not in out and "STALE" not in out, out

# An observed delta with no entry fails.
counts, out = run([seen(), seen(trial="trial-2")], [entry()])
assert counts == (1, 0), counts
assert "UNEXPLAINED" in out and "trial-2" in out

# An entry that no longer occurs fails.
counts, out = run([], [entry()])
assert counts == (0, 1), counts
assert "STALE" in out

# A listed delta whose observed value differs does not explain it: both lists fail.
counts, _ = run([seen(observed=None)], [entry()])
assert counts == (1, 1), counts
counts, _ = run([seen(saved=False)], [entry()])
assert counts == (1, 1), counts

# An entry of another check does not explain, and is not stale for this one.
counts, _ = run([seen()], [entry(check="reproduce")])
assert counts == (1, 0), counts
counts, _ = run([], [entry(check="reproduce")])
assert counts == (0, 0), counts

# Replaying part of the saved trials does not make the entries of the others stale.
two = [entry(run="a", task="t1"), entry(run="a", task="t2"), entry(run="b", task="t1")]
assert len(kd.reconcile("replay", [], two)[2]) == 3
only = kd.reconcile("replay", [], two, scope={("a", "t1")})[2]
assert [(e["run"], e["task"]) for e in only] == [("a", "t1")], only
assert kd.reconcile("replay", [], two, scope={("c", "t9")})[2] == []

# observed_varies accepts any observed value that still differs from the saved one.
varies = entry(field="key_fingerprint:actual", saved="AAAA", observed="<varies>", observed_varies=True,
               cause="mirror_key_regenerated")
counts, _ = run([seen(field="key_fingerprint:actual", saved="AAAA", observed="BBBB")], [varies])
assert counts == (0, 0), counts
counts, _ = run([seen(field="key_fingerprint:actual", saved="AAAA", observed="AAAA")], [varies])
assert counts == (1, 1), counts

# The file is validated: unknown cause, missing evidence, duplicates, missing keys.
def loads(entries):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "k.json"
        path.write_text(json.dumps(entries))
        return kd.load(path)

assert loads([entry()]) == [entry()]
for bad in (entry(cause="flaky"), entry(evidence=""), entry(check="selftest")):
    try:
        loads([bad])
    except kd.KnownDeltaError:
        pass
    else:
        raise AssertionError(bad)
try:
    loads([entry(), entry()])
except kd.KnownDeltaError:
    pass
else:
    raise AssertionError("duplicate accepted")
missing = entry()
del missing["added_in"]
try:
    loads([missing])
except kd.KnownDeltaError:
    pass
else:
    raise AssertionError("missing key accepted")
assert kd.load(pathlib.Path("/nonexistent/known-deltas.json")) == []

# The committed file loads and every cause is one the code names.
committed = kd.load()
assert all(item["cause"] in kd.CAUSES for item in committed)

# Leaf diff: equal values give no delta, a changed leaf gives its path, a list is one leaf.
assert kd.leaf_diff({"a": {"b": 1}}, {"a": {"b": 1}}) == []
assert kd.leaf_diff({"a": {"b": 1}}, {"a": {"b": 2}}) == [("a.b", 1, 2)]
assert kd.leaf_diff({"a": [1, 2]}, {"a": [1]}) == [("a", [1, 2], [1])]
assert kd.leaf_diff({"a": 1}, {"a": 1, "c": 3}) == [("c", None, 3)]

# replay_deltas: the same stable fields as before, now with saved and observed values.
def verdict(goal, claims):
    return {"goal": {"pass": goal}, "frame": {"pass": True}, "fixed": goal,
            "claims": {"per_claim": claims}}

saved = verdict(True, {"a": {"correct": True, "actual": 1}, "x_pid": {"correct": True, "actual": 5},
                       "diagnostic_commands": {"correct": False, "actual": ["x"]}})
fresh = verdict(False, {"a": {"correct": True, "actual": 2}, "x_pid": {"correct": False, "actual": 9},
                        "diagnostic_commands": {"correct": True, "actual": []}})
got = {d["field"]: (d["saved"], d["observed"]) for d in replay_deltas(saved, fresh)}
assert got == {"goal": (True, False), "fixed": (True, False), "a:actual": (1, 2),
               "diagnostic_commands": (False, True)}, got
assert replay_agrees(saved, fresh) == (False, ["goal", "fixed", "a:actual", "diagnostic_commands"])
assert replay_agrees(saved, saved) == (True, [])
print("known deltas: OK")
