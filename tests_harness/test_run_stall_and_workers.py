"""Provider-stall rule and the helpers behind `make run --workers`. No Harbor, no Docker, no keys."""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness import cli, storage
from harness.report import exclude_reason
from harness.terminus_pin import PROVIDER_STALL_SEC, call_latency_summary, is_provider_stall


def test_latency_summary():
    assert call_latency_summary([]) == (None, None)
    assert call_latency_summary([{"finish_reason": "stop"}]) == (None, None)
    assert call_latency_summary([{"latency_sec": 2.5}, {"latency_sec": 10.0}, {}]) == (10.0, 12.5)


def test_stall_threshold_is_300_seconds_and_inclusive():
    assert PROVIDER_STALL_SEC == 300.0
    assert not is_provider_stall({"max_call_latency_sec": 299.999})
    assert is_provider_stall({"max_call_latency_sec": 300.0})
    assert is_provider_stall({"max_call_latency_sec": 1078.0})
    assert not is_provider_stall({"max_call_latency_sec": None})
    assert not is_provider_stall({})


def test_stalled_trial_is_reported_as_excluded_provider_stall():
    meta = {"stop_reason": "infra_error", "excluded": True, "exclude_reason": "provider_stall"}
    assert exclude_reason(meta) == "provider_stall"


def test_stalled_attempt_is_kept_beside_the_rerun():
    old = storage.RUNS
    with tempfile.TemporaryDirectory() as tmp:
        storage.RUNS = pathlib.Path(tmp)
        try:
            base = storage.RUNS / "r" / "t" / storage.slug("m")
            (base / "trial-2").mkdir(parents=True)
            (base / "trial-2" / "meta.json").write_text(json.dumps({"exclude_reason": "provider_stall"}))
            moved = cli._keep_stalled_attempt("r", "t", "m", 2)
            assert moved.name == "trial-2-provider_stall" and (moved / "meta.json").is_file()
            assert not (base / "trial-2").exists()
            (base / "trial-2").mkdir()
            assert cli._keep_stalled_attempt("r", "t", "m", 2).name == "trial-2-provider_stall2"
        finally:
            storage.RUNS = old


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("stall and workers helpers: OK")
