"""Pinned seeds, a per-trial cost cap, and two OpenRouter workers with the poller on.

No Docker and no key. The poller is a fake. Overlapping trials must not take the
key-usage delta as one trial's cost.
"""
import contextlib, io, json, os, pathlib, sys, tempfile, threading, types
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import cli, env, openrouter_spend, storage

GEMINI = """session_budget_usd = {limit}
max_trial_cost_usd = {cap}

[[models]]
label = "fake-gemini"
provider = "gemini"
model = "fake"
temperature = 1.0
reasoning_effort = "high"
price_table = {{ input = 2.0, cached_input = 0.1, output = 10.0, read = "2026-11-07", valid_until = "2999-01-01", source = "test" }}

[pinned_trial_seeds]
t1 = [11]
"""

OPENROUTER = """session_budget_usd = 5.0

[[models]]
label = "fake-or"
provider = "openrouter"
model = "fake"
temperature = 1.0
reasoning_effort = "high"
"""


class FakeTask:
    def __init__(self, tid):
        self.id = tid
        self.harness = {"feasible_seed_modulus": 2, "feasible_seed_remainder": 0}


def _run(root, config, run_live, tasks, trials, workers, provider_env, poll=None):
    saved = (env.Task, env.build, storage.RUNS, cli._write_run_report, sys.modules.get("harness.terminus_runner"))
    old = os.environ.get(provider_env)
    old_poller = openrouter_spend.session_poller
    try:
        env.Task, env.build = FakeTask, lambda task: None
        storage.RUNS = pathlib.Path(root) / "runs"
        cli._write_run_report = lambda run_id: None
        sys.modules["harness.terminus_runner"] = types.SimpleNamespace(run_live=run_live)
        os.environ[provider_env] = "placeholder-not-a-key"
        poll = poll or (lambda: {"spent_usd": 0.2})
        openrouter_spend.session_poller = lambda state_path, limit, fetch=None: poll
        cfg = pathlib.Path(root) / "c.toml"
        cfg.write_text(config)
        args = types.SimpleNamespace(
            config=str(cfg), models="", tasks=tasks, trials=trials, seed=1, run_id="r", workers=workers,
        )
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cli.cmd_run(args)
        lines = [json.loads(line) for line in out.getvalue().splitlines() if line.startswith("{")]
        return rc, lines, err.getvalue()
    finally:
        env.Task, env.build, storage.RUNS, cli._write_run_report, mod = saved
        if mod is None:
            sys.modules.pop("harness.terminus_runner", None)
        else:
            sys.modules["harness.terminus_runner"] = mod
        openrouter_spend.session_poller = old_poller
        if old is None:
            os.environ.pop(provider_env, None)
        else:
            os.environ[provider_env] = old


def test_pinned_seed_is_not_stratified():
    calls = []

    def run_live(task, m, run_id, trial, seed):
        calls.append(seed)
        meta = {"steps": 1, "stop_reason": "agent_done", "excluded": False, "usage": {"cost_usd": 0.01}}
        return {"reward": 0}, meta

    with tempfile.TemporaryDirectory() as tmp:
        rc, lines, err = _run(tmp, GEMINI.format(limit=5.0, cap=5.0), run_live, "t1", 1, 1, "GEMINI_API_KEY")
    assert rc == 0, (rc, lines, err)
    assert calls == [11], calls


def test_a_trial_over_the_cap_stops_the_run():
    calls = []

    def run_live(task, m, run_id, trial, seed):
        calls.append(trial)
        meta = {"steps": 1, "stop_reason": "agent_done", "excluded": False, "usage": {"cost_usd": 0.90}}
        return {"reward": 0}, meta

    config = GEMINI.format(limit=5.0, cap=0.80).replace("t1 = [11]", "t1 = [11, 12]")
    with tempfile.TemporaryDirectory() as tmp:
        rc, lines, err = _run(tmp, config, run_live, "t1", 2, 1, "GEMINI_API_KEY")
    assert rc == 2, (rc, lines, err)
    assert calls == [1], calls
    assert any(line.get("stop") == "trial_cost" for line in lines), lines


def test_overlapping_trials_do_not_take_the_key_delta():
    barrier = threading.Barrier(2)
    calls = []

    def run_live(task, m, run_id, trial, seed):
        calls.append(task.id)
        try:
            barrier.wait(timeout=2)
        except threading.BrokenBarrierError:
            pass
        meta = {
            "steps": 1, "stop_reason": "agent_done", "excluded": False,
            "usage": {"cost_usd": 0.0},
            "llm_calls_detail": [{"provider_cost_usd": 0.11}],
        }
        directory = storage.RUNS / run_id / task.id / m["label"] / f"trial-{trial}"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "meta.json").write_text(json.dumps(meta))
        (directory / "grade.json").write_text("{}")
        return {"reward": 0}, meta

    config = OPENROUTER + "\n[pinned_trial_seeds]\nt1 = [4]\nt2 = [5]\n"
    with tempfile.TemporaryDirectory() as tmp:
        rc, lines, err = _run(tmp, config, run_live, "t1,t2", 1, 2, "OPENROUTER_API_KEY")
        assert "cannot attribute" not in err, err
        assert rc == 0, (rc, lines, err)
        assert sorted(calls) == ["t1", "t2"]
        sources = []
        for tid in ("t1", "t2"):
            meta = json.loads((pathlib.Path(tmp) / "runs" / "r" / tid / "fake-or" / "trial-1" / "meta.json").read_text())
            sources.append((meta["usage"].get("cost_usd_source"), meta["usage"].get("cost_usd")))
        assert sources == [("provider_response_cost", 0.11), ("provider_response_cost", 0.11)], sources
        blob = json.dumps(lines) + err
        assert "placeholder-not-a-key" not in blob


def test_one_openrouter_trial_still_uses_the_key_delta():
    def run_live(task, m, run_id, trial, seed):
        meta = {"steps": 1, "stop_reason": "agent_done", "excluded": False, "usage": {"cost_usd": 0.0}}
        directory = storage.RUNS / run_id / task.id / m["label"] / f"trial-{trial}"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "meta.json").write_text(json.dumps(meta))
        (directory / "grade.json").write_text("{}")
        return {"reward": 0}, meta

    config = OPENROUTER + "\n[pinned_trial_seeds]\nt1 = [4]\n"
    spent = {"value": 0.0}

    def poll():
        spent["value"] += 0.2
        return {"spent_usd": spent["value"]}

    with tempfile.TemporaryDirectory() as tmp:
        rc, lines, err = _run(tmp, config, run_live, "t1", 1, 2, "OPENROUTER_API_KEY", poll)
        meta = json.loads((pathlib.Path(tmp) / "runs" / "r" / "t1" / "fake-or" / "trial-1" / "meta.json").read_text())
    assert rc == 0, (rc, lines, err)
    assert meta["usage"]["cost_usd_source"] == "openrouter_key_usage_delta"
    assert meta["usage"]["cost_usd"] == 0.2


if __name__ == "__main__":
    test_pinned_seed_is_not_stratified()
    test_a_trial_over_the_cap_stops_the_run()
    test_overlapping_trials_do_not_take_the_key_delta()
    test_one_openrouter_trial_still_uses_the_key_delta()
    print("openrouter workers: OK")
