"""A trial keeps the recorder's raw bytes and per-call latency. No Docker, no Harbor."""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from harness.terminus_pin import RAW_TRACE_CAP_BYTES, RAW_TRACE_FILES, call_latency_summary, save_raw_trace


class FakeContainer:
    def __init__(self, files):
        self.files = files
        self.asked = []

    def read_file(self, path):
        self.asked.append(path)
        return self.files.get(path)


def test_raw_trace_and_history_are_copied_with_sizes():
    box = FakeContainer({"/logs/agent/executed.trace": "#0#ls\0+ ls\n", "/logs/agent/executed.commands": "ls\n"})
    with tempfile.TemporaryDirectory() as tmp:
        saved = save_raw_trace(tmp, box)
        assert (pathlib.Path(tmp) / "executed.trace").read_bytes() == b"#0#ls\0+ ls\n"
        assert (pathlib.Path(tmp) / "executed.commands").read_text() == "ls\n"
    assert saved["executed.trace"] == {"present": True, "bytes": 11, "bytes_seen": 11, "capped": False}
    assert box.asked == [path for _name, path in RAW_TRACE_FILES]


def test_a_cap_is_applied_and_recorded():
    big = "x" * (RAW_TRACE_CAP_BYTES + 10)
    with tempfile.TemporaryDirectory() as tmp:
        saved = save_raw_trace(tmp, FakeContainer({"/logs/agent/executed.trace": big}))
        assert (pathlib.Path(tmp) / "executed.trace").stat().st_size == RAW_TRACE_CAP_BYTES
    assert saved["executed.trace"]["capped"] is True
    assert saved["executed.trace"]["bytes_seen"] == RAW_TRACE_CAP_BYTES + 10


def test_a_missing_file_is_recorded_as_missing():
    with tempfile.TemporaryDirectory() as tmp:
        saved = save_raw_trace(tmp, FakeContainer({}))
        assert not (pathlib.Path(tmp) / "executed.trace").exists()
    assert saved["executed.commands"]["present"] is False


def test_latency_fields_summarise_the_call_records():
    records = [{"latency_sec": 1.5, "t_request": "a", "t_response": "b"}, {"latency_sec": 945.25}]
    assert call_latency_summary(records) == (945.25, 946.75)


def test_runner_writes_the_fields_it_is_tested_for():
    src = (pathlib.Path(__file__).resolve().parent.parent / "harness" / "terminus_runner.py").read_text()
    for needle in ('"t_request"', '"latency_sec"', "max_call_latency_sec", "save_raw_trace(td.path, container)",
                   "**storage.spec_stamp(task.dir)", "provider_stall"):
        assert needle in src, needle


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("trial artifacts: OK")
