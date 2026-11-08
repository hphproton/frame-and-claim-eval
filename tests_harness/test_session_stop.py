"""SessionBudget stops `make run` when trial costs add up past the limit. Fake cost, no Docker, no key.

The live path is replaced by a stub whose meta carries usage.cost_usd, the field the
price table fills for Gemini. The environment variable is a placeholder, never a key.
"""
import contextlib, io, json, os, pathlib, sys, tempfile, threading, types
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import cli, env, storage

CONFIG = """session_budget_usd = {limit}

[[models]]
label = "fake-gemini"
provider = "gemini"
model = "fake"
temperature = 1.0
reasoning_effort = "high"
price_table = {{ input = 2.0, cached_input = 0.1, output = 10.0, read = "2026-11-07", valid_until = "2999-01-01", source = "test" }}
"""


def run(limit, cost, trials, workers, tasks="t1,t2"):
    calls = []
    lock = threading.Lock()

    def run_live(task, m, run_id, trial, seed):
        with lock:
            calls.append((task.id, trial, seed))
        meta = {"steps": 1, "stop_reason": "agent_done", "excluded": False, "usage": {"cost_usd": cost}}
        return {"fixed": True, "truthful": True, "overclaim": False, "reward": 1}, meta

    class FakeTask:
        def __init__(self, tid):
            self.id = tid

    saved = (env.Task, env.build, storage.RUNS, cli._write_run_report, sys.modules.get("harness.terminus_runner"))
    old_key = os.environ.get("GEMINI_API_KEY")
    tmp = tempfile.TemporaryDirectory()
    try:
        env.Task, env.build = FakeTask, lambda task: None
        storage.RUNS = pathlib.Path(tmp.name) / "runs"
        cli._write_run_report = lambda run_id: None
        sys.modules["harness.terminus_runner"] = types.SimpleNamespace(run_live=run_live)
        os.environ["GEMINI_API_KEY"] = "placeholder-not-a-key"
        cfg = pathlib.Path(tmp.name) / "c.toml"
        cfg.write_text(CONFIG.format(limit=limit))
        args = types.SimpleNamespace(config=str(cfg), models="", tasks=tasks, trials=trials, seed=1, run_id="r", workers=workers)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli.cmd_run(args)
        lines = [json.loads(line) for line in out.getvalue().splitlines() if line.startswith("{")]
        return rc, calls, lines
    finally:
        env.Task, env.build, storage.RUNS, cli._write_run_report, mod = saved
        if mod is None:
            sys.modules.pop("harness.terminus_runner", None)
        else:
            sys.modules["harness.terminus_runner"] = mod
        if old_key is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = old_key
        tmp.cleanup()


def test_one_worker_stops_before_the_trial_that_would_pass_the_limit():
    rc, calls, lines = run(limit=0.10, cost=0.04, trials=5, workers=1)
    assert rc == 2, rc
    assert len(calls) == 2, calls  # 0.04 + 0.04 = 0.08; a third would reach 0.12
    assert any(line.get("stop") == "budget" for line in lines), lines


def test_a_budget_that_covers_every_trial_runs_them_all():
    rc, calls, lines = run(limit=10.0, cost=0.04, trials=3, workers=1)
    assert rc == 0 and len(calls) == 6, (rc, len(calls))
    assert not any(line.get("stop") in ("budget", "budget_unknown") for line in lines)


def test_three_workers_stop_and_overshoot_by_at_most_the_trials_in_flight():
    rc, calls, lines = run(limit=0.10, cost=0.04, trials=5, workers=3)
    assert rc == 2, rc
    assert len(calls) <= 2 + 3, calls  # at most workers-1 started on a stale total
    assert len(calls) < 10, "the budget did not stop the run"
    assert any(line.get("stop") == "budget" for line in lines), lines


def test_seeds_do_not_depend_on_workers():
    _, one, _ = run(limit=10.0, cost=0.0, trials=2, workers=1)
    _, three, _ = run(limit=10.0, cost=0.0, trials=2, workers=3)
    assert sorted(one) == sorted(three)


def test_no_key_value_is_printed():
    _, _, lines = run(limit=10.0, cost=0.0, trials=1, workers=1)
    assert "placeholder-not-a-key" not in json.dumps(lines)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("session stop: OK")
