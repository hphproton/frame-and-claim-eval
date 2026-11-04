"""Count Terminus JSON problems from a dumped trajectory.

Hard parse failures and AUTO-CORRECTED warnings are different events. The
failure count is the one already stored as terminus_json_format_failures.
The warning count is separate. Both come from the trajectory file, so a trial
that dies after the dump still has the counts that were written.
"""
import json, pathlib


def count_trajectory(trajectory):
    errors = 0
    auto = 0
    for step in trajectory.get("steps") or []:
        observation = step.get("observation") or {}
        for result in observation.get("results") or []:
            content = result.get("content") or ""
            if not isinstance(content, str):
                continue
            if content.startswith("Previous response had parsing errors:"):
                errors += 1
            auto += content.count("AUTO-CORRECTED:")
    return {"errors": errors, "autocorrected": auto}


def count_file(path):
    path = pathlib.Path(path)
    if not path.is_file():
        return {"errors": 0, "autocorrected": 0, "present": False}
    counts = count_trajectory(json.loads(path.read_text()))
    counts["present"] = True
    return counts


def apply_trajectory_counts(meta, path):
    """Write the file's counts onto the trial.

    A dumped trajectory is the source of truth. A caller that defaulted the
    failure count to 0 before this runs does not keep that 0 when the file
    records failures. A missing file leaves the meta dict alone.
    """
    counts = count_file(path)
    if counts["present"]:
        meta["terminus_json_format_failures"] = counts["errors"]
        meta["terminus_json_autocorrected"] = counts["autocorrected"]
    return counts
