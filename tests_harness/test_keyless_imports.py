"""Keyless commands must not import Harbor.

Run with system Python, not .venv. `make test-harness` does that.
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def test_keyless_modules_do_not_import_harbor():
    import harness.agent
    import harness.cli
    import harness.grading
    import harness.replay
    import harness.report
    import harness.reproduce
    assert "harbor" not in sys.modules
    assert "harness.terminus_runner" not in sys.modules
    assert harness.cli.cmd_run is not None


if __name__ == "__main__":
    test_keyless_modules_do_not_import_harbor()
    print("keyless import checks: OK")
