"""JSON-failure and AUTO-CORRECTED counts from a trajectory, no Harbor."""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from harness.trajectory_counts import apply_trajectory_counts, count_file, count_trajectory


def _step(content):
    return {"observation": {"results": [{"content": content}]}}


def test_hard_failure_and_autocorrect_are_separate():
    trajectory = {"steps": [
        _step("Previous response had parsing errors:\nERROR: not json"),
        _step("Previous response had warnings:\nWARNINGS: AUTO-CORRECTED: missing braces - please fix"),
        _step("command output"),
    ]}
    counts = count_trajectory(trajectory)
    assert counts == {"errors": 1, "autocorrected": 1}


def test_missing_file_is_zero_and_present_false():
    missing = pathlib.Path(tempfile.mkdtemp()) / "trajectory.json"
    assert count_file(missing) == {"errors": 0, "autocorrected": 0, "present": False}


def test_file_with_a_failure_is_not_zero():
    directory = pathlib.Path(tempfile.mkdtemp())
    path = directory / "trajectory.json"
    path.write_text(json.dumps({"steps": [
        _step("Previous response had parsing errors:\nERROR: nope"),
    ]}))
    assert count_file(path)["errors"] == 1
    assert count_file(path)["present"] is True


def test_apply_overwrites_a_default_zero():
    directory = pathlib.Path(tempfile.mkdtemp())
    path = directory / "trajectory.json"
    path.write_text(json.dumps({"steps": [
        _step("Previous response had parsing errors:\nERROR: nope"),
        _step("Previous response had warnings:\nWARNINGS: AUTO-CORRECTED: missing braces - please fix"),
    ]}))
    meta = {"terminus_json_format_failures": 0}
    apply_trajectory_counts(meta, path)
    assert meta["terminus_json_format_failures"] == 1
    assert meta["terminus_json_autocorrected"] == 1


def test_missing_file_does_not_invent_a_zero():
    meta = {}
    apply_trajectory_counts(meta, pathlib.Path(tempfile.mkdtemp()) / "trajectory.json")
    assert "terminus_json_format_failures" not in meta


if __name__ == "__main__":
    test_hard_failure_and_autocorrect_are_separate()
    test_missing_file_is_zero_and_present_false()
    test_file_with_a_failure_is_not_zero()
    test_apply_overwrites_a_default_zero()
    test_missing_file_does_not_invent_a_zero()
    print("trajectory count checks: OK")
