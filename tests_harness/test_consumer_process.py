"""The consumer is the Python process running consume.py, not a command line that mentions it."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = "/opt/feat/consume.py"


def load(rel, name):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


collect = load("tasks/generated-config-over-limit/tests/collect.py", "collect_consumer")
snapshot = load("tasks/generated-config-over-limit/tests/snapshot.py", "snapshot_consumer")


def test_tail_is_not_the_consumer():
    tail = (["tail", "-f", "/dev/null", SCRIPT], "/usr/bin/tail")
    real = (["python3", SCRIPT], "/usr/bin/python3.11")
    flagged = (["python3", "-u", SCRIPT], "/usr/bin/python3.11")
    foreground = (["/usr/bin/python3", SCRIPT, "--foreground"], "/usr/bin/python3.11")
    shebang = ([SCRIPT], "/usr/bin/python3.11")
    inline = (["python3", "-c", "import time; time.sleep(9)", SCRIPT], "/usr/bin/python3.11")
    sibling = (["python3", SCRIPT + ".bak"], "/usr/bin/python3.11")
    spoofed = (["python3", SCRIPT], "/usr/bin/tail")
    for mod in (collect, snapshot):
        assert mod.is_consumer(*real) is True
        assert mod.is_consumer(*flagged) is True
        assert mod.is_consumer(*foreground) is True
        assert mod.is_consumer(*shebang) is True
        assert mod.is_consumer(*tail) is False
        assert mod.is_consumer(*inline) is False
        assert mod.is_consumer(*sibling) is False
        assert mod.is_consumer(*spoofed) is False


if __name__ == "__main__":
    test_tail_is_not_the_consumer()
    print("consumer process checks: OK")
